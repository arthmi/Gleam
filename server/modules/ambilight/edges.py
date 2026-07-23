#ambilight/edge.py
from enum import Enum
import numpy as np

class Edge(Enum):
    TOP = "top"
    BOTTOM = "bottom"
    LEFT = "left"
    RIGHT = "right"


def extract_edge_band(image: np.ndarray, edge: Edge, band_depth_percent: float) -> np.ndarray:
    height, width = image.shape[:2]

    if edge in (Edge.TOP, Edge.BOTTOM):
        band_depth_px = int(height * band_depth_percent)
    else:
        band_depth_px = int(width * band_depth_percent)

    match edge:
        case Edge.TOP:
            band = image[:band_depth_px, :, :]
        case Edge.BOTTOM:
            band = image[-band_depth_px:, :, :]
            band = band[::-1, :, :]  # reverse depth axis so index 0 = outermost pixel
        case Edge.LEFT:
            band = image[:, :band_depth_px, :]
            band = np.transpose(band, (1, 0, 2))  # (depth, length, 3)
        case Edge.RIGHT:
            band = image[:, -band_depth_px:, :]
            band = np.transpose(band, (1, 0, 2))
            band = band[::-1, :, :]
        case _:
            raise ValueError(f"Unknown edge: {edge}")
    return band


def compute_weighted_colors(band: np.ndarray, weight_exponent: float) -> np.ndarray:
    depth = band.shape[0]
    # weight[0] (edge pixel) = 1.0, decreasing to ~0 at the innermost pixel.
    weights = (1 - np.arange(depth) / depth) ** weight_exponent
    weights = weights / weights.sum()

    # np.average with weights broadcasts weights over axis 0.
    return np.average(band, axis=0, weights=weights)


def downsample_to_led_count(colors: np.ndarray, led_count: int) -> np.ndarray:
    chunks = np.array_split(colors, led_count, axis=0)
    return np.array([chunk.mean(axis=0) for chunk in chunks])


def get_edge_colors(
        frame: np.ndarray,
        edge: Edge,
        band_depth_percent: float,
        led_count: int,
        reversed_: bool,
        weight_exponent: float,
        blur_sigma: float
    ) -> np.ndarray:
    band = extract_edge_band(frame, edge, band_depth_percent)
    colors = compute_weighted_colors(band, weight_exponent)
    colors = apply_spatial_blur(colors, blur_sigma)
    result = downsample_to_led_count(colors, led_count)
    if reversed_:
        result = result[::-1]
    return result

def apply_spatial_blur(colors: np.ndarray, sigma: float) -> np.ndarray:
    if sigma <= 0:
        return colors
    kernel = gaussian_kernel(sigma)
    radius = len(kernel) // 2
    colors = colors.astype(np.float32)
    blurred = np.empty_like(colors)
    for c in range(colors.shape[1]):
        padded = np.pad(colors[:, c], (radius, radius), mode='edge')
        blurred[:, c] = np.convolve(padded, kernel, mode='valid')
    return blurred

def gaussian_kernel(sigma: float) -> np.ndarray:
    radius = int(np.ceil(3 * sigma))
    x = np.arange(-radius, radius + 1)
    kernel = np.exp(-(x**2) / (2 * sigma**2))
    kernel /= kernel.sum()
    return kernel