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
        
        
@dataclass(frozen=True, slots=True)
class ChordResult:
    # Vectorized chord length along x (same for all rows inside the cylinder’s vertical span)
    Lx: np.ndarray                 # shape: (width,)
    # 2D chord map (broadcasted along y only within cylinder vertical extent)
    chord_map: np.ndarray          # shape: (height, width)
    # Boolean mask where chord_map is valid (inside cylinder’s vertical span and |x-center_x|<=radius)
    mask: np.ndarray               # shape: (height, width)
    # Simple stats for quick logging
    stats: dict   
        
        
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
    
    
def show_detection(
    image: np.ndarray,
    geometry: CylinderGeometry,
    diagnostics: Optional[DetectionDiagnostics] = None,
    *,
    figsize: Tuple[int, int] = (12, 10),
) -> None:
    """Optional visualization kept separate from detection logic."""
    fig, axes = plt.subplots(2, 2, figsize=figsize)

    # 1) Original with bounds
    ax = axes[0, 0]
    ax.imshow(image, cmap="gray")
    ax.axvline(geometry.left_edge, color="r", linestyle="--", linewidth=2, label="Left")
    ax.axvline(geometry.right_edge, color="g", linestyle="--", linewidth=2, label="Right")
    ax.axhline(geometry.top_edge, color="b", linestyle="--", linewidth=2, label="Top")
    ax.axhline(geometry.bottom_edge, color="y", linestyle="--", linewidth=2, label="Bottom")
    ax.plot(geometry.center_x, geometry.center_y, "ro", markersize=8, label="Center")
    ax.set_title("Detected Cylinder Geometry")
    ax.legend(loc="upper right")
    ax.axis("off")

    # 2) Edge magnitude crop
    if diagnostics and diagnostics.edges_mag is not None:
        ax = axes[0, 1]
        ax.imshow(diagnostics.edges_mag, cmap="hot")
        rect = plt.Rectangle(
            (geometry.left_edge, geometry.top_edge),
            geometry.width,
            geometry.height,
            fill=False, color="c", linewidth=2, label="Detected Region",
        )
        ax.add_patch(rect)
        ax.set_title("Edge Magnitude + Region")
        ax.legend()
        ax.axis("off")
    else:
        axes[0, 1].axis("off")

    # 3) Horizontal profile
    if diagnostics and diagnostics.horizontal_profile_smooth is not None:
        ax = axes[1, 0]
        prof = diagnostics.horizontal_profile_smooth
        ax.plot(prof, label="Smoothed Horizontal Profile")
        if diagnostics.peaks is not None:
            ax.plot(diagnostics.peaks, prof[diagnostics.peaks], "ro", label="Peaks")
        ax.set_xlabel("X (pixels)")
        ax.set_ylabel("Edge strength")
        ax.set_title("Horizontal Profile")
        ax.grid(True, alpha=0.3)
        ax.legend()
    else:
        axes[1, 0].axis("off")

    # 4) Vertical profile and counts
    if diagnostics and diagnostics.vertical_edge_profile is not None:
        ax = axes[1, 1]
        vprof = diagnostics.vertical_edge_profile
        vcount = diagnostics.vertical_edge_count
        ax.plot(vprof, np.arange(len(vprof)), "b-", label="Max Edge Strength")
        if vcount is not None and vcount.max() > 0:
            ax.plot(
                (vcount / vcount.max()) * (vprof.max() if vprof.max() > 0 else 1.0),
                np.arange(len(vcount)),
                "r--", alpha=0.7, label="Edge Count (scaled)",
            )
        ax.axhline(geometry.top_edge, color="b", linestyle=":", linewidth=2, label=f"Top ({geometry.top_edge})")
        ax.axhline(geometry.bottom_edge, color="y", linestyle=":", linewidth=2, label=f"Bottom ({geometry.bottom_edge})")
        ax.set_ylabel("Y (pixels)")
        ax.set_xlabel("Edge strength / count")
        ax.set_title("Vertical Edge Analysis")
        ax.grid(True, alpha=0.3)
        ax.invert_yaxis()
        ax.legend()
    else:
        axes[1, 1].axis("off")

    plt.tight_layout()
    plt.show()
    
    
def chord_length_profile_x(
    width: int,
    center_x: int,
    outer_radius: int,
    *,
    is_hollow: bool = False,
    inner_radius: Optional[int] = None,
    edge_epsilon: float = 0.0,
) -> np.ndarray:
    """
    Compute the 1D chord length profile L(x) for a vertical cylinder.

    For a solid cylinder:
        L(x) = 2 * sqrt(R^2 - (x - center_x)^2)   for |x - center_x| <= R
             = 0                                   otherwise

    For a hollow cylinder:
        L(x) = L_outer(x) - L_inner(x), clipped at >= 0

    Parameters
    ----------
    width : int
        Width of the image in pixels.
    center_x : int
        Horizontal coordinate of the cylinder center (in pixels).
    outer_radius : int
        Outer radius of the cylinder in pixels.
    is_hollow : bool, optional
        If True, compute profile for a hollow cylinder. Default is False.
    inner_radius : int, optional
        Inner radius (in pixels) for hollow cylinder. Ignored if
        `is_hollow` is False.
    edge_epsilon : float, optional
        Minimum chord length value to enforce for numerical stability.
        Values 0 < L < edge_epsilon are clipped to edge_epsilon.
        Useful only if the profile will be used in divisions. Default is 0.

    Returns
    -------
    L : ndarray of shape (width,)
        1D chord length profile across the image columns.
    """
    x = np.arange(width, dtype=np.float64)
    dx = x - float(center_x)

    outer_sq = np.maximum(0.0, float(outer_radius) ** 2 - dx**2)
    L_outer = 2.0 * np.sqrt(outer_sq)

    if not is_hollow:
        L = L_outer
    else:
        if inner_radius is None:
            raise ValueError("inner_radius must be provided when is_hollow=True")
        inner_sq = np.maximum(0.0, float(inner_radius) ** 2 - dx**2)
        L_inner = 2.0 * np.sqrt(inner_sq)
        L = np.maximum(0.0, L_outer - L_inner)

    if edge_epsilon > 0.0:
        small_pos = (L > 0.0) & (L < edge_epsilon)
        L = L.copy()
        L[small_pos] = edge_epsilon

    return L


def calculate_cylindrical_chord_map(
    image_shape: Tuple[int, int],
    *,
    center_x: int,
    top_edge: int,
    bottom_edge: int,
    radius: int,
    is_hollow: bool = False,
    inner_radius: Optional[int] = None,
    outside_fill: Literal["zero", "nan"] = "zero",
    edge_epsilon: float = 0.0,
) -> ChordResult:
    """
    Calculate the chord length profile and 2D map for a vertical cylinder.

    The chord length map represents the physical path length through the
    cylinder at each horizontal position. For an upright cylinder, the
    chord length depends only on `x`, and is broadcast vertically between
    `top_edge` and `bottom_edge`.

    Parameters
    ----------
    image_shape : tuple of int
        Shape of the image as (height, width).
    center_x : int
        Horizontal coordinate of the cylinder center (in pixels).
    top_edge : int
        Top edge (row index) of the cylinder bounding box.
    bottom_edge : int
        Bottom edge (row index) of the cylinder bounding box.
    radius : int
        Outer radius of the cylinder in pixels.
    is_hollow : bool, optional
        If True, compute chord lengths for a hollow cylinder. Default is False.
    inner_radius : int, optional
        Inner radius in pixels (used only if `is_hollow=True`).
    outside_fill : {"zero", "nan"}, optional
        Value assigned outside the cylinder region in the returned map.
        Default is "zero".
    edge_epsilon : float, optional
        Minimum chord length value to enforce for numerical stability.
        Useful if chord lengths will later appear in denominators.
        Default is 0.

    Returns
    -------
    result : ChordResult
        A dataclass with fields:

        - Lx : ndarray of shape (width,)
            1D chord length profile along the horizontal axis.
        - chord_map : ndarray of shape (height, width)
            2D chord length map with outside filled as 0 or NaN.
        - mask : ndarray of bool, shape (height, width)
            Boolean mask indicating valid cylinder pixels.
        - stats : dict
            Summary statistics (min, max, mean inside the cylinder, etc.).

    Notes
    -----
    - Outside the cylinder, the chord length is physically zero. Setting it to
      NaN (`outside_fill="nan"`) can be safer for debugging, as invalid regions
      will not contribute silently to calculations.
    - The `mask` should be used to restrict subsequent operations (e.g.,
      attenuation fitting or geometry correction) to valid pixels.
    """
    height, width = image_shape

    Lx = chord_length_profile_x(
        width=width,
        center_x=center_x,
        outer_radius=radius,
        is_hollow=is_hollow,
        inner_radius=inner_radius,
        edge_epsilon=edge_epsilon,
    )

    col_mask = Lx > 0.0
    row_mask = np.zeros(height, dtype=bool)
    row_mask[max(0, top_edge):min(height, bottom_edge + 1)] = True

    mask = np.outer(row_mask, col_mask)

    if outside_fill == "nan":
        chord_map = np.full((height, width), np.nan, dtype=np.float64)
    else:
        chord_map = np.zeros((height, width), dtype=np.float64)

    chord_map[row_mask, :] = Lx

    valid_vals = chord_map[mask]
    stats = {
        "shape": chord_map.shape,
        "valid_pixels": int(mask.sum()),
        "min_inside": float(np.nanmin(valid_vals)) if valid_vals.size else np.nan,
        "max_inside": float(np.nanmax(valid_vals)) if valid_vals.size else np.nan,
        "mean_inside": float(np.nanmean(valid_vals)) if valid_vals.size else np.nan,
        "radius": int(radius),
        "diameter": int(2 * radius),
        "type": "hollow" if is_hollow else "solid",
        "outside_fill": outside_fill,
    }

    return ChordResult(Lx=Lx, chord_map=chord_map, mask=mask, stats=stats)