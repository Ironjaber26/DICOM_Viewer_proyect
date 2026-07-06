"""Helpers to turn raw DICOM pixel data into a viewable image array."""

from typing import Optional, Tuple

import numpy as np
from pydicom.dataset import FileDataset


def get_pixel_array(ds: FileDataset) -> np.ndarray:
    """Return the pixel data with rescale slope/intercept applied.

    Many CT/PET images store raw stored values that must be converted
    to real-world units (e.g. Hounsfield Units for CT) using:

        real_value = stored_value * RescaleSlope + RescaleIntercept
    """
    array = ds.pixel_array.astype(np.float64)
    slope = float(getattr(ds, "RescaleSlope", 1))
    intercept = float(getattr(ds, "RescaleIntercept", 0))
    return array * slope + intercept


def apply_windowing(
    array: np.ndarray,
    window_center: Optional[float] = None,
    window_width: Optional[float] = None,
    ds: Optional[FileDataset] = None,
) -> np.ndarray:
    """Apply DICOM windowing (contrast) and normalize to 0-255 uint8.

    If ``window_center``/``window_width`` are not given explicitly, they
    are read from ``ds`` (``WindowCenter``/``WindowWidth`` tags). If
    neither is available, min/max of the array is used instead.
    """
    if window_center is None and ds is not None:
        wc = getattr(ds, "WindowCenter", None)
        window_center = float(wc[0] if isinstance(wc, (list, tuple)) else wc) if wc is not None else None
    if window_width is None and ds is not None:
        ww = getattr(ds, "WindowWidth", None)
        window_width = float(ww[0] if isinstance(ww, (list, tuple)) else ww) if ww is not None else None

    if window_center is None or window_width is None:
        low, high = array.min(), array.max()
    else:
        low = window_center - window_width / 2
        high = window_center + window_width / 2

    clipped = np.clip(array, low, high)
    if high == low:
        return np.zeros_like(clipped, dtype=np.uint8)

    normalized = (clipped - low) / (high - low) * 255.0
    return normalized.astype(np.uint8)


def get_image_shape(ds: FileDataset) -> Tuple[int, ...]:
    """Return the shape the pixel array will have once loaded."""
    return ds.pixel_array.shape
