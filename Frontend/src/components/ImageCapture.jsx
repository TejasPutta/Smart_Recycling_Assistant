import { useCallback, useEffect, useRef, useState } from "react";
import NeonButton from "./NeonButton.jsx";
import TrackingFrame from "./TrackingFrame.jsx";
import { validateImage } from "../api/client";
import "./ImageCapture.css";

const LIVE_INTERVAL_MS = 2500; // how often live scan sends a frame

function describeCameraError(err) {
  switch (err?.name) {
    case "NotAllowedError":
    case "PermissionDeniedError":
      return "Camera access was blocked. Allow it in the browser's address bar, or upload an image.";
    case "NotFoundError":
    case "DevicesNotFoundError":
      return "No camera was found on this device. Upload an image instead.";
    case "NotReadableError":
      return "The camera is being used by another app. Close it and try again.";
    default:
      return "Couldn't start the camera. Upload an image instead.";
  }
}

// Crop the camera image to the area inside the tracking frame, so what the user
// puts inside the frame is exactly what gets classified.
function grabFrame(video, box) {
  const vw = video.videoWidth;
  const vh = video.videoHeight;
  if (!vw || !vh) return Promise.resolve(null);

  const frameEl = box?.querySelector(".tracking-frame");
  const fraction = frameEl && box.offsetWidth ? Math.min(1, frameEl.offsetWidth / box.offsetWidth) : 0.62;

  // The camera box is 4:3 and the video fills it, so only this much width is visible.
  const visibleWidth = Math.min(vw, vh * (4 / 3));
  const side = Math.round(Math.min(Math.min(vw, vh), visibleWidth * fraction));
  const sx = Math.round((vw - side) / 2);
  const sy = Math.round((vh - side) / 2);
  const out = Math.min(side, 512);

  const canvas = document.createElement("canvas");
  canvas.width = out;
  canvas.height = out;
  canvas.getContext("2d").drawImage(video, sx, sy, side, side, 0, 0, out, out);
  return new Promise((resolve) => canvas.toBlob(resolve, "image/jpeg", 0.88));
}

/**
 * Camera + upload + tracking frame.
 * Calls onCapture(blobOrFile, { kind: "manual" | "live" | "upload" }).
 */
export default function ImageCapture({
  frameState,
  frameLabel,
  busy,
  paused,
  previewUrl,
  onCapture,
  onBackToCamera,
}) {
  const videoRef = useRef(null);
  const boxRef = useRef(null);
  const streamRef = useRef(null);
  const fileRef = useRef(null);
  const busyRef = useRef(busy);

  const [camera, setCamera] = useState("off"); // "off" | "starting" | "on"
  const [liveOn, setLiveOn] = useState(false);
  const [message, setMessage] = useState(null);

  useEffect(() => {
    busyRef.current = busy;
  }, [busy]);

  const stopCamera = useCallback(() => {
    streamRef.current?.getTracks().forEach((track) => track.stop());
    streamRef.current = null;
    if (videoRef.current) videoRef.current.srcObject = null;
    setCamera("off");
    setLiveOn(false);
  }, []);

  // Release the camera when leaving the page
  useEffect(() => stopCamera, [stopCamera]);

  const startCamera = async () => {
    setMessage(null);
    if (!navigator.mediaDevices?.getUserMedia) {
      setMessage("This browser can't open the camera on this address. Use localhost or https, or upload an image.");
      return;
    }
    setCamera("starting");
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { facingMode: { ideal: "environment" }, width: { ideal: 1280 }, height: { ideal: 720 } },
        audio: false,
      });
      streamRef.current = stream;
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play().catch(() => {});
      }
      setCamera("on");
    } catch (err) {
      setCamera("off");
      setMessage(describeCameraError(err));
    }
  };

  const captureNow = useCallback(
    async (kind) => {
      const video = videoRef.current;
      if (!video || camera !== "on") return;
      const blob = await grabFrame(video, boxRef.current);
      if (blob) onCapture(blob, { kind });
    },
    [camera, onCapture]
  );

  // Live scan: send a frame every few seconds while the previous one is finished
  useEffect(() => {
    if (!liveOn || camera !== "on" || paused || previewUrl) return undefined;
    const id = setInterval(() => {
      if (!busyRef.current) captureNow("live");
    }, LIVE_INTERVAL_MS);
    return () => clearInterval(id);
  }, [liveOn, camera, paused, previewUrl, captureNow]);

  const toggleLive = () => {
    const next = !liveOn;
    setLiveOn(next);
    if (next && !busy) captureNow("live");
  };

  const onFileChange = (event) => {
    const file = event.target.files?.[0];
    event.target.value = ""; // allows picking the same file again
    if (!file) return;
    const problem = validateImage(file);
    if (problem) {
      setMessage(problem);
      return;
    }
    setMessage(null);
    onCapture(file, { kind: "upload" });
  };

  const showVideo = camera === "on" && !previewUrl;
  const showFrame = showVideo || !!previewUrl;

  let statusText = "Camera off";
  if (previewUrl) statusText = "Uploaded image";
  else if (camera === "starting") statusText = "Starting camera";
  else if (camera === "on") statusText = liveOn ? "Live scan on" : "Camera ready";

  return (
    <div className="stack">
      <div className="camera-box" ref={boxRef}>
        <video ref={videoRef} hidden={!showVideo} playsInline muted autoPlay />
        {previewUrl && <img className="camera-still" src={previewUrl} alt="Uploaded item" />}

        {!showFrame && (
          <div className="camera-empty">
            <div>
              <h3>Camera is off</h3>
              <p>Start the camera and hold an item inside the frame, or upload a photo.</p>
            </div>
          </div>
        )}

        {showFrame && <TrackingFrame state={frameState} label={frameLabel} />}

        <div className="camera-hud">
          <span className="hud-chip">
            {liveOn && showVideo && <span className="live-dot" aria-hidden="true" />}
            {statusText}
          </span>
          {busy && <span className="hud-chip">Analysing</span>}
        </div>
      </div>

      <p className="sr-only" role="status">
        {frameLabel || ""}
      </p>

      {message && (
        <div className="inline-alert inline-alert--info" role="alert">
          {message}
        </div>
      )}

      <div className="row">
        {camera === "off" && !previewUrl && (
          <NeonButton solid onClick={startCamera}>
            Start camera
          </NeonButton>
        )}
        {camera === "starting" && (
          <NeonButton solid disabled>
            Starting camera
          </NeonButton>
        )}
        {showVideo && (
          <>
            <NeonButton solid onClick={() => captureNow("manual")} disabled={busy || paused}>
              Scan now
            </NeonButton>
            <NeonButton solid={liveOn} onClick={toggleLive} aria-pressed={liveOn} disabled={paused}>
              {liveOn ? "Live scan on" : "Live scan off"}
            </NeonButton>
          </>
        )}
        {previewUrl && (
          <NeonButton solid onClick={onBackToCamera}>
            {camera === "on" ? "Back to camera" : "Close image"}
          </NeonButton>
        )}
        <NeonButton onClick={() => fileRef.current?.click()} disabled={busy}>
          Upload image
        </NeonButton>
        {camera === "on" && (
          <NeonButton color="amber" size="sm" onClick={stopCamera}>
            Stop camera
          </NeonButton>
        )}
        <input
          ref={fileRef}
          type="file"
          accept="image/jpeg,image/png,image/webp"
          hidden
          onChange={onFileChange}
        />
      </div>
    </div>
  );
}
