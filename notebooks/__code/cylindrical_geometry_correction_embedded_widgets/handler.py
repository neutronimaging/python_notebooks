# Standard library
from dataclasses import dataclass
from glob import glob
import os
from pathlib import Path
from typing import Any, Dict, Iterable, List, Literal, Optional, Sequence, Tuple
from pprint import pprint
from ipywidgets import interactive
from IPython.display import display
import ipywidgets as widgets
import logging

# Third-party libraries
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.patches as patches
from matplotlib import colors
import numpy as np
from pydantic import BaseModel, Field, field_validator, model_validator
from scipy import ndimage, stats
from scipy.ndimage import gaussian_filter1d, median_filter
from scipy.signal import find_peaks, savgol_filter
# from tifffile import imread
# from astropy.io import fits

from tqdm.auto import tqdm

from notebooks.__code.cylindrical_geometry_correction_embedded_widgets.utilities import replace_nan_with_local_median


class CylinderGeometry(BaseModel):
    """
    Cylindrical geometry in pixel coordinates (origin: top-left).
    Only store primitives; derive the rest via properties.
    """
    left_edge: int = Field(..., ge=0)
    right_edge: int = Field(..., ge=0)
    top_edge: int = Field(..., ge=0)
    bottom_edge: int = Field(..., ge=0)
    center_x: int = Field(..., ge=0)
    center_y: int = Field(..., ge=0)

    @model_validator(mode="after")
    def _validate_bounds(self):
        if self.right_edge <= self.left_edge:
            raise ValueError("right_edge must be > left_edge")
        if self.bottom_edge <= self.top_edge:
            raise ValueError("bottom_edge must be > top_edge")
        return self

    @property
    def width(self) -> int:
        return self.right_edge - self.left_edge

    @property
    def height(self) -> int:
        return self.bottom_edge - self.top_edge + 1

    @property
    def radius(self) -> int:
        return self.width // 2

    def __str__(self) -> str:
        return (
            "CylinderGeometry(\n"
            f"  Boundaries: left={self.left_edge}, right={self.right_edge}, "
            f"top={self.top_edge}, bottom={self.bottom_edge}\n"
            f"  Center: ({self.center_x}, {self.center_y})\n"
            f"  Dimensions: width={self.width}, height={self.height}, radius={self.radius}\n"
            ")"
        )
        
        
@dataclass(slots=True)
class DetectionConfig:
    # horizontal (left/right)
    peak_threshold: float = 0.30   # fraction of max
    peak_distance: int = 20
    smooth_sigma: float = 2.0
    # vertical (top/bottom)
    edge_percentile: float = 90.0
    min_edge_pixels_per_row: int = 3
    # diagnostics
    diagnostics: bool = False


@dataclass(slots=True)
class DetectionDiagnostics:
    edges_x: Optional[np.ndarray] = None
    edges_y: Optional[np.ndarray] = None
    edges_mag: Optional[np.ndarray] = None
    horizontal_profile_smooth: Optional[np.ndarray] = None
    peaks: Optional[np.ndarray] = None
    edge_threshold: Optional[float] = None
    vertical_edge_profile: Optional[np.ndarray] = None
    vertical_edge_count: Optional[np.ndarray] = None


def detect_cylindrical_boundary(
    image: np.ndarray,
    config: Optional[DetectionConfig] = None,
) -> tuple[CylinderGeometry, Optional[DetectionDiagnostics]]:
    """
    Detect cylindrical sample region in a 2D float image.

    Parameters
    ----------
    image : np.ndarray
        2D float array (preprocessed radiograph; e.g., summed over TOF).
    config : DetectionConfig, optional
        Tunables for detection and diagnostics.

    Returns
    -------
    (geometry, diagnostics)
        geometry : CylinderGeometry
        diagnostics : DetectionDiagnostics or None
    """
    if config is None:
        config = DetectionConfig()

    # --- input checks (fast & strict) ---
    if not isinstance(image, np.ndarray):
        raise ValueError("image must be a numpy array")
    if image.ndim != 2:
        raise ValueError(f"image must be 2D, got {image.ndim}D")
    if not np.issubdtype(image.dtype, np.floating):
        raise ValueError(f"image must be float dtype, got {image.dtype}")
    if image.size == 0:
        raise ValueError("image is empty")

    diag = DetectionDiagnostics() if config.diagnostics else None

    # --- edges ---
    edges_x = ndimage.sobel(image, axis=1)  # vertical edge response (for left/right)
    edges_y = ndimage.sobel(image, axis=0)  # horizontal edge response (for top/bottom)
    edges_mag = np.hypot(edges_x, edges_y)

    if diag:
        diag.edges_x = edges_x
        diag.edges_y = edges_y
        diag.edges_mag = edges_mag

    # --- left/right via horizontal profile ---
    horizontal_profile = np.sum(np.abs(edges_x), axis=0)
    horizontal_profile_smooth = gaussian_filter1d(horizontal_profile, sigma=config.smooth_sigma)
    peak_height = float(horizontal_profile_smooth.max()) * config.peak_threshold
    peaks, _ = find_peaks(
        horizontal_profile_smooth, height=peak_height, distance=config.peak_distance
    )
    if diag:
        diag.horizontal_profile_smooth = horizontal_profile_smooth
        diag.peaks = peaks

    if peaks.size < 2:
        raise ValueError(
            f"Could not detect cylinder edges. Only {peaks.size} peak(s) found. "
            "Adjust peak_threshold or peak_distance."
        )

    # Choose two strongest peaks
    peak_strengths = horizontal_profile_smooth[peaks]
    strongest = peaks[np.argsort(peak_strengths)[::-1][:2]]
    left_edge, right_edge = int(min(strongest)), int(max(strongest))
    center_x = (left_edge + right_edge) // 2

    # --- top/bottom inside the detected lateral window ---
    col_slice = slice(left_edge, right_edge + 1)
    edges_cropped = edges_mag[:, col_slice]
    # Row-wise max response inside the cylinder columns
    vertical_edge_profile = edges_cropped.max(axis=1)

    # Percentile threshold and count per row
    nonzero = edges_mag > 0
    edge_thresh = float(np.percentile(edges_mag[nonzero], config.edge_percentile))
    edge_count_per_row = np.sum(edges_cropped > edge_thresh, axis=1)

    if diag:
        diag.edge_threshold = edge_thresh
        diag.vertical_edge_profile = vertical_edge_profile
        diag.vertical_edge_count = edge_count_per_row

    rows = np.where(edge_count_per_row >= config.min_edge_pixels_per_row)[0]
    if rows.size > 0:
        top_edge, bottom_edge = int(rows.min()), int(rows.max())
    else:
        # fallback: any edge activity
        nz = np.where(vertical_edge_profile > 0)[0]
        if nz.size > 0:
            top_edge, bottom_edge = int(nz.min()), int(nz.max())
        else:
            # final fallback: full height
            top_edge, bottom_edge = 0, image.shape[0] - 1

    center_y = (top_edge + bottom_edge) // 2

    geometry = CylinderGeometry(
        left_edge=left_edge,
        right_edge=right_edge,
        top_edge=top_edge,
        bottom_edge=bottom_edge,
        center_x=center_x,
        center_y=center_y,
    )
    return geometry, diag


def replace_with_nans(images):
    logging.info(f"Checking for NaN values in the hyperspectral stack of shape {images.shape} and dtype {images.dtype}")
# Check for NaN values and replace with local median if found
    cleaned_images = np.empty_like(images)
    
    for _index, _image in enumerate(images):
        
        logging.info(f"\tProcessing image {_index + 1}/{len(images)}")
        if np.isnan(_image).any():
            logging.info("\\ttWarning: NaN values found in the hyperspectral stack.")
            num_nan_initial = np.sum(np.isnan(_image))
            logging.info(f"\t\tTotal NaN values found: {num_nan_initial}")

            # Replace NaN values with local median using a 3x3x3 kernel (default)
            # You can adjust the kernel size based on your data characteristics
            # Larger kernels will provide more smoothing but may blur fine details
            _image = replace_nan_with_local_median(
                _image, 
                kernel_size=(3, 3, 3)  # (height, width, spectral_dimension)
            )
            # Verify replacement
            num_nan_final = np.sum(np.isnan(_image))
            logging.info(f"\t\tFinal verification: {num_nan_final} NaN values remaining")
            cleaned_images[_index] = _image
            
        else:
            logging.info("\tNo NaN values found in the hyperspectral stack.")

        cleaned_images[_index] = _image

    return cleaned_images


def display_edges(geometry: CylinderGeometry, diagnostics: Optional[DetectionDiagnostics] = None):
    fig, ax = plt.subplots(ncols=2, nrows=3, figsize=(10, 10))
    # ax.plot(diagnostics.edges_x[50, :])
    ax[0, 0].imshow(diagnostics.edges_x, cmap='gray', aspect='auto')
    ax[0, 0].set_title('Edges X')
    # ax[0, 1].imshow(diagnostics.edges_y, cmap='gray', aspect='auto')
    # ax[0, 1].set_title('Edges Y')
    ax[0, 1].imshow(diagnostics.edges_mag, cmap='gray', aspect='auto')
    ax[0, 1].set_title('Edges Magnitude')

    horizontal_profile = np.sum(np.abs(diagnostics.edges_x), axis=0)
    ax[1, 0].plot(horizontal_profile, label='Raw Profile')  
    horizontal_profile_smooth = gaussian_filter1d(horizontal_profile, sigma=2.0)
    ax[1, 1].plot(horizontal_profile_smooth, label='Smoothed Profile', color='orange')

    ax[2, 0].plot(diagnostics.vertical_edge_profile, label='Vertical Edge Profile')
    ax[2, 0].set_title('Vertical Edge Profile')
    ax[2, 1].plot(diagnostics.vertical_edge_count, label='Vertical Edge Count', color='green')  
    ax[2, 1].set_title('Vertical Edge Count')

    plt.tight_layout()
    