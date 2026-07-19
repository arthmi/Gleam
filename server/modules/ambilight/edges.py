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
        weight_exponent: float = 2.0,
    ) -> np.ndarray:
    band = extract_edge_band(frame, edge, band_depth_percent)
    colors = compute_weighted_colors(band, weight_exponent)
    result = downsample_to_led_count(colors, led_count)

    if reversed_:
        result = result[::-1]

    return result