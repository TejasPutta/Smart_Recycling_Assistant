import { useCallback, useEffect, useRef, useState } from "react";

import DropletAnimation from "../components/DropletAnimation.jsx";
import GuidancePanel from "../components/GuidancePanel.jsx";
import ImageCapture from "../components/ImageCapture.jsx";
import PredictionList from "../components/PredictionList.jsx";
import ResultCard from "../components/ResultCard.jsx";
import { awardDroplets, classifyImage, getGuidance, saveScan } from "../api/client";
import {
  CONFIDENCE_LOCK_THRESHOLD,
  canConfirmScan,
  formatConfidence,
  getFrameState,
} from "../utils/categories";
import "./ScanPage.css";

export default function ScanPage() {
  const [result, setResult] = useState(null); // response of POST /classify
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [previewUrl, setPreviewUrl] = useState(null);

  const [guidance, setGuidance] = useState({ status: "idle" });
  const [guidanceTry, setGuidanceTry] = useState(0);

  const [saving, setSaving] = useState(false);
  const [saved, setSaved] = useState(null); // { id, created_at }
  const [award, setAward] = useState(null); // response of POST /rewards/award
  const [saveError, setSaveError] = useState(null);
  const [burst, setBurst] = useState(null);

  // Used to ignore answers from requests that are no longer the latest one.
  const seqRef = useRef(0);
  const guidanceCache = useRef(new Map());
  const previewRef = useRef(null);

  const top = result?.predictions?.[0] ?? null;
  const frameState = getFrameState(top, result?.source);

  // ---------- Image preview (uploads) ----------
  const replacePreview = (url) => {
    if (previewRef.current) URL.revokeObjectURL(previewRef.current);
    previewRef.current = url;
    setPreviewUrl(url);
  };
  useEffect(
    () => () => {
      if (previewRef.current) URL.revokeObjectURL(previewRef.current);
    },
    []
  );

  // ---------- Classify ----------
  const handleCapture = useCallback(async (image, meta) => {
    const seq = ++seqRef.current;
    setBusy(true);
    setError(null);
    if (meta.kind === "upload") replacePreview(URL.createObjectURL(image));

    try {
      const data = await classifyImage(image);
      if (seq !== seqRef.current) return;
      setResult(data);
      setSaved(null);
      setAward(null);
      setSaveError(null);
    } catch (err) {
      if (seq !== seqRef.current) return;
      setError(err.message);
    } finally {
      if (seq === seqRef.current) setBusy(false);
    }
  }, []);

  const resetSession = useCallback(() => {
    seqRef.current += 1;
    setBusy(false);
    setResult(null);
    setError(null);
    setSaved(null);
    setAward(null);
    setSaveError(null);
    setGuidance({ status: "idle" });
  }, []);

  const handleBackToCamera = () => {
    replacePreview(null);
    resetSession();
  };

  const handleScanAnother = () => {
    replacePreview(null);
    resetSession();
  };

  // ---------- Guidance (only for confident, real model results) ----------
  const lockedKey =
    top && result?.source === "model" && top.confidence >= CONFIDENCE_LOCK_THRESHOLD
      ? `${top.label}|${top.category}`
      : null;

  useEffect(() => {
    if (!lockedKey) {
      setGuidance({ status: "idle" });
      return undefined;
    }
    const cached = guidanceCache.current.get(lockedKey);
    if (cached) {
      setGuidance({ status: "ready", data: cached });
      return undefined;
    }

    let cancelled = false;
    setGuidance({ status: "loading" });
    // Short delay so live scanning doesn't call Gemini for every passing item.
    const timer = setTimeout(async () => {
      try {
        const data = await getGuidance({
          label: top.label,
          category: top.category,
          confidence: top.confidence,
        });
        if (cancelled) return;
        if (data.source === "gemini") guidanceCache.current.set(lockedKey, data);
        setGuidance({ status: "ready", data });
      } catch (err) {
        if (!cancelled) setGuidance({ status: "error", error: err.message });
      }
    }, 700);

    return () => {
      cancelled = true;
      clearTimeout(timer);
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [lockedKey, guidanceTry]);

  // ---------- Confirm disposal: save, then award droplets ----------
  const awardFor = async (scanId) => {
    try {
      const awarded = await awardDroplets(scanId);
      setAward(awarded);
      if (awarded.awarded) setBurst({ id: Date.now(), amount: awarded.amount });
      setSaveError(null);
    } catch (err) {
      setSaveError(`Scan saved, but droplets could not be awarded: ${err.message}`);
    }
  };

  const handleConfirm = async () => {
    if (!result || !top || saving || saved || !canConfirmScan(result.source, top)) return;

    seqRef.current += 1; // ignore any scan still in flight
    setBusy(false);
    setSaving(true);
    setSaveError(null);

    try {
      const savedScan = await saveScan({
        label: top.label,
        category: top.category,
        confidence: top.confidence,
        source: result.source,
        predictions: result.predictions,
      });
      setSaved(savedScan);
      await awardFor(savedScan.id);
    } catch (err) {
      setSaveError(err.message);
    } finally {
      setSaving(false);
    }
  };

  // ---------- Tracking frame label ----------
  const lowConfidence = !!top && result?.source === "model" && top.confidence < CONFIDENCE_LOCK_THRESHOLD;
  let frameLabel = null;
  if (frameState !== "scanning") frameLabel = `${top.label} ${formatConfidence(top.confidence)}`;
  else if (result?.source === "demo") frameLabel = "AI offline";
  else if (lowConfidence) frameLabel = "Not sure yet";
  else if (busy) frameLabel = "Scanning";

  return (
    <div className="page">
      <DropletAnimation burst={burst} />

      <div className="page-head">
        <h1>Scan an item</h1>
        <p>Hold it inside the frame. Green means recyclable, red means hazardous.</p>
      </div>

      <div className="scan-grid">
        <ImageCapture
          frameState={frameState}
          frameLabel={frameLabel}
          busy={busy}
          paused={saving || !!saved}
          previewUrl={previewUrl}
          onCapture={handleCapture}
          onBackToCamera={handleBackToCamera}
        />

        <div className="stack">
          {error && (
            <div className="inline-alert" role="alert">
              {error}
            </div>
          )}

          {result && top ? (
            <>
              <ResultCard
                result={result}
                top={top}
                canConfirm={canConfirmScan(result.source, top)}
                saving={saving}
                saved={saved}
                award={award}
                saveError={saveError}
                onConfirm={handleConfirm}
                onRetryAward={() => saved && awardFor(saved.id)}
                onReset={handleScanAnother}
              />
              <GuidancePanel
                status={guidance.status}
                data={guidance.data}
                error={guidance.error}
                onRetry={() => setGuidanceTry((n) => n + 1)}
              />
              <PredictionList predictions={result.predictions} />
            </>
          ) : (
            !error && (
              <section className="panel empty-state">
                <h3>No scan yet</h3>
                <p>
                  Start the camera or upload a photo. The result, recycling steps and your droplet
                  reward show up here.
                </p>
              </section>
            )
          )}
        </div>
      </div>
    </div>
  );
}
