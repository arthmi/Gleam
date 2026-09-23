# pipeline.py
import numpy as np
import cv2

def extract_band(frame: np.ndarray, edge: str, band_depth_percent: float) -> np.ndarray:
    match edge:
        case "top":
            band_depth = int(band_depth_percent * frame.shape[0])
            band = frame[0:band_depth, :, :]
        case "bottom":
            band_depth = int(band_depth_percent * frame.shape[0])
            band = frame[-band_depth:, :, :]
        case "left":
            band_depth = int(band_depth_percent * frame.shape[1])
            band = frame[:, 0:band_depth, :]
        case "right":
            band_depth = int(band_depth_percent * frame.shape[1])
            band = frame[:, -band_depth:, :]
        case _:
            raise ValueError(f"Unknown edge: {edge!r} (expected 'top', 'bottom', 'left', or 'right')")
    return band

def sample_led_colors(
        band: np.ndarray,
        edge: str,
        num_leds: int,
        weight_exponent: int,
        sample_overlap_percent: float,
    ) -> np.ndarray:
    match edge:
        case "top" | "bottom":
            long_axis_length = band.shape[1]
            short_axis = 0
            depth = band.shape[0]
            reverse_weights = (edge == "bottom")
        case "left" | "right":
            long_axis_length = band.shape[0]
            short_axis = 1
            depth = band.shape[1]
            reverse_weights = (edge == "right")
        case _:
            raise ValueError(f"Unknown edge: {edge!r} (expected 'top', 'bottom', 'left', or 'right')")

    distances = np.linspace(0, 1, depth)
    if reverse_weights:
        distances = distances[::-1]
    weights = (1 - distances) ** weight_exponent

    seg_width = long_axis_length / num_leds
    overlap_px = seg_width * sample_overlap_percent

    output = np.zeros((num_leds, 3))
    for i in range(num_leds):
        base_start = i * seg_width
        base_end = (i + 1) * seg_width

        window_start = max(0, base_start - overlap_px)
        window_end = min(long_axis_length, base_end + overlap_px)

        start_idx = int(round(window_start))
        end_idx = int(round(window_end))

        match edge:
            case "top" | "bottom":
                window = band[:, start_idx:end_idx, :]
            case "left" | "right":
                window = band[start_idx:end_idx, :, :]

        row_colors = np.average(window, axis=short_axis, weights=weights)
        output[i] = row_colors.mean(axis=0)

    return output

def apply_saturation_boost(colors: np.ndarray, saturation_boost: float) -> np.ndarray:
    num_leds = colors.shape[0]
    img = np.clip(colors, 0, 255).astype(np.uint8).reshape(1, num_leds, 3)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1].astype(np.float64) * saturation_boost, 0, 255).astype(np.uint8)

    rgb = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
    return rgb.reshape(num_leds, 3)

class TemporalSmoother:
    def __init__(self, num_leds: int, tau: float):
        self.num_leds: int = num_leds
        self.tau: float = tau
        self._prev_colors: np.ndarray | None = None

    def smooth(self, raw_colors: np.ndarray, dt: float) -> np.ndarray:
        if not self.tau:
            return raw_colors
        alpha = 1 - np.exp(-dt / self.tau)
        if self._prev_colors is None:
            self._prev_colors = raw_colors
            return raw_colors
        blended = alpha * raw_colors + (1 - alpha) * self._prev_colors
        self._prev_colors = blended
        return blended

    def reset(self) -> None:
        self._prev_colors = None