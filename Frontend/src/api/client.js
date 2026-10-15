// Single place for every backend call.
// Base URL comes from .env (VITE_API_URL). All routes live under /api/v1.

const BASE_URL = (
  import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api/v1"
).replace(/\/+$/, "");

export const USER_ID = import.meta.env.VITE_USER_ID || "user-1";

export const MAX_UPLOAD_BYTES = 8 * 1024 * 1024; // backend limit: 8 MB
export const ALLOWED_TYPES = ["image/jpeg", "image/png", "image/webp"];

export class ApiError extends Error {
  constructor(message, status = 0) {
    super(message);
    this.name = "ApiError";
    this.status = status; // 0 = could not reach the backend
  }
}

// FastAPI errors look like { detail: "message" } or { detail: [{ msg }, ...] }
function readDetail(body, fallback) {
  if (!body || body.detail == null) return fallback;
  if (typeof body.detail === "string") return body.detail;
  if (Array.isArray(body.detail)) {
    return body.detail.map((d) => d.msg).filter(Boolean).join(", ") || fallback;
  }
  return fallback;
}

async function request(path, { method = "GET", body, form, timeoutMs = 15000 } = {}) {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const options = { method, signal: controller.signal, headers: {} };
  if (form) {
    options.body = form; // browser sets the multipart boundary itself
  } else if (body !== undefined) {
    options.headers["Content-Type"] = "application/json";
    options.body = JSON.stringify(body);
  }

  let response;
  try {
    response = await fetch(`${BASE_URL}${path}`, options);
  } catch (err) {
    if (err.name === "AbortError") {
      throw new ApiError("The backend took too long to answer. Try again.");
    }
    throw new ApiError(
      "Can't reach the backend. Check that it is running on " + BASE_URL
    );
  } finally {
    clearTimeout(timer);
  }

  let data = null;
  try {
    data = await response.json();
  } catch {
    // empty or non-JSON body
  }

  if (!response.ok) {
    throw new ApiError(
      readDetail(data, `Request failed (${response.status})`),
      response.status
    );
  }
  return data;
}

function toQuery(params = {}) {
  const query = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value !== undefined && value !== null && value !== "") {
      query.append(key, value);
    }
  });
  const text = query.toString();
  return text ? `?${text}` : "";
}

// Check a file before uploading so errors are instant and clear.
// Returns an error message, or null if the file is fine.
export function validateImage(file) {
  if (!file) return "No image selected.";
  if (!ALLOWED_TYPES.includes(file.type)) {
    return "Unsupported image type. Use JPEG, PNG or WebP.";
  }
  if (file.size > MAX_UPLOAD_BYTES) {
    return "Image is larger than 8 MB. Use a smaller one.";
  }
  if (file.size === 0) return "The image is empty.";
  return null;
}

// ---------- Health / status ----------
export const getHealth = () => request("/health");
export const getClassifierStatus = () => request("/classify/status");

// ---------- Classification ----------
// `image` can be a File (upload) or a Blob (camera capture).
// The first request can be slow: the backend may download model weights.
export function classifyImage(image, { timeoutMs = 60000 } = {}) {
  const problem = validateImage(image);
  if (problem) return Promise.reject(new ApiError(problem, 400));

  const form = new FormData();
  form.append("file", image, image.name || "capture.jpg");
  return request("/classify", { method: "POST", form, timeoutMs });
}

// ---------- Guidance ----------
export const getGuidance = ({ label, category, confidence }) =>
  request("/guidance", {
    method: "POST",
    body: { label, category, confidence },
    timeoutMs: 30000, // Gemini can take a few seconds
  });

// ---------- History ----------
// Only call after the user explicitly confirms.
export const saveScan = ({ label, category, confidence, source, predictions }) =>
  request("/history", {
    method: "POST",
    body: { label, category, confidence, source, predictions },
  });

export const getHistory = ({ limit = 20, offset = 0, category } = {}) =>
  request(`/history${toQuery({ limit, offset, category })}`);

export const getScanDetail = (id) => request(`/history/${id}`);

// ---------- Statistics + virtual bins ----------
export const getStatistics = () => request("/statistics");
export const getBins = () => request("/bins");

// ---------- Rewards ----------
export const getRewardBalance = (userId = USER_ID) =>
  request(`/rewards/balance${toQuery({ user_id: userId })}`);

export const awardDroplets = (scanId, reason = "confirmed disposal", userId = USER_ID) =>
  request("/rewards/award", {
    method: "POST",
    body: { user_id: userId, scan_id: scanId, reason },
  });

export const getRewardHistory = ({ limit = 20, offset = 0, userId = USER_ID } = {}) =>
  request(`/rewards/history${toQuery({ user_id: userId, limit, offset })}`);
