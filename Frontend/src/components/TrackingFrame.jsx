/**
 * The object-tracking frame drawn over the camera.
 *
 * state:
 *   "scanning" -> searching (breathing frame + moving scan line)
 *   "green"    -> eco-friendly / recyclable category locked
 *   "red"      -> hazardous category locked
 *   "amber"    -> locked, but the category is unknown
 *
 * The backend only classifies a whole image (no bounding boxes), so this frame
 * is fixed in the centre. ImageCapture crops the camera image to the area inside
 * this frame, so what you put inside the frame is what gets scanned.
 */
export default function TrackingFrame({ state = "scanning", label = null }) {
  return (
    <div className={`tracking-frame tracking-frame--${state}`} aria-hidden="true">
      <span className="tf-corner tf-corner--tl" />
      <span className="tf-corner tf-corner--tr" />
      <span className="tf-corner tf-corner--bl" />
      <span className="tf-corner tf-corner--br" />
      {state === "scanning" && <span className="tf-scanline" />}
      {label && <span className="tf-label">{label}</span>}
    </div>
  );
}
