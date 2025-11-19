
"""
Utility functions for PyNBIS.
"""

from typing import Union, Tuple
import numpy as np
import numpy.typing as npt
from pathlib import Path


def load_fingerprint(filepath: Union[str, Path]) -> npt.NDArray[np.uint8]:
    """
    Load a fingerprint image from file.
    
    Supports common image formats (PNG, JPEG, BMP, etc.) via PIL/Pillow.
    
    Args:
        filepath: Path to image file
    
    Returns:
        Grayscale image as uint8 numpy array
    
    Raises:
        ImportError: If PIL/Pillow is not installed
        FileNotFoundError: If file doesn't exist
        ValueError: If image format is unsupported
    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("PIL/Pillow is required for image loading. Install with: pip install Pillow")
    
    filepath = Path(filepath)
    if not filepath.exists():
        raise FileNotFoundError(f"File not found: {filepath}")
    
    img = Image.open(filepath)
    
    # Convert to grayscale
    if img.mode != 'L':
        img = img.convert('L')
    
    return np.array(img, dtype=np.uint8)


def save_fingerprint(image: npt.NDArray[np.uint8], 
                    filepath: Union[str, Path]) -> None:
    """
    Save a fingerprint image to file.
    
    Args:
        image: Grayscale image as uint8 numpy array
        filepath: Path to save the image
    
    Raises:
        ImportError: If PIL/Pillow is not installed
    """
    try:
        from PIL import Image
    except ImportError:
        raise ImportError("PIL/Pillow is required for image saving. Install with: pip install Pillow")
    
    img = Image.fromarray(image, mode='L')
    img.save(filepath)


def normalize_image(image: npt.NDArray, 
                   target_mean: float = 127.0,
                   target_std: float = 64.0) -> npt.NDArray[np.uint8]:
    """
    Normalize a fingerprint image to target mean and standard deviation.
    
    Args:
        image: Input image (any dtype)
        target_mean: Target mean value (default: 127)
        target_std: Target standard deviation (default: 64)
    
    Returns:
        Normalized image as uint8 array
    """
    img_float = image.astype(np.float64)
    
    # Current statistics
    current_mean = np.mean(img_float)
    current_std = np.std(img_float)
    
    # Avoid division by zero
    if current_std < 1e-6:
        return np.full_like(image, int(target_mean), dtype=np.uint8)
    
    # Normalize
    normalized = (img_float - current_mean) / current_std
    normalized = normalized * target_std + target_mean
    
    # Clip and convert
    normalized = np.clip(normalized, 0, 255)
    return normalized.astype(np.uint8)


def resize_fingerprint(image: npt.NDArray[np.uint8],
                      target_ppi: int = 500,
                      source_ppi: int = 500) -> npt.NDArray[np.uint8]:
    """
    Resize a fingerprint image to match target PPI.
    
    Args:
        image: Input fingerprint image
        target_ppi: Target pixels per inch
        source_ppi: Source pixels per inch
    
    Returns:
        Resized image
    
    Raises:
        ImportError: If scipy is not installed
    """
    if source_ppi == target_ppi:
        return image
    
    try:
        from scipy import ndimage
    except ImportError:
        raise ImportError("scipy is required for image resizing. Install with: pip install scipy")
    
    scale_factor = target_ppi / source_ppi
    new_shape = (int(image.shape[0] * scale_factor), 
                 int(image.shape[1] * scale_factor))
    
    return ndimage.zoom(image, scale_factor, order=1).astype(np.uint8)


def visualize_minutiae(image: npt.NDArray[np.uint8],
                      minutiae: list,
                      marker_size: int = 10) -> npt.NDArray[np.uint8]:
    """
    Visualize minutiae on fingerprint image.
    
    Creates a color image with minutiae marked.
    
    Args:
        image: Grayscale fingerprint image
        minutiae: List of Minutia objects
        marker_size: Size of minutiae markers
    
    Returns:
        Color image with minutiae visualized
    
    Raises:
        ImportError: If matplotlib or opencv is not available
    """
    try:
        import cv2
    except ImportError:
        raise ImportError("opencv-python is required for visualization. Install with: pip install opencv-python")
    
    # Convert to color
    vis_image = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)
    
    for minutia in minutiae:
        x, y = minutia.x, minutia.y
        
        # Different colors for different types
        if minutia.minutia_type.value == 0:  # Ridge ending
            color = (0, 255, 0)  # Green
        else:  # Bifurcation
            color = (0, 0, 255)  # Red
        
        # Draw circle
        cv2.circle(vis_image, (x, y), marker_size, color, 2)
        
        # Draw direction line
        direction_rad = minutia.direction * np.pi / 180
        dx = int(marker_size * 2 * np.cos(direction_rad))
        dy = int(marker_size * 2 * np.sin(direction_rad))
        cv2.line(vis_image, (x, y), (x + dx, y + dy), color, 2)
    
    return vis_image


def get_roi(image: npt.NDArray[np.uint8],
           threshold: int = 16) -> Tuple[int, int, int, int]:
    """
    Estimate region of interest (ROI) in fingerprint image.
    
    Args:
        image: Grayscale fingerprint image
        threshold: Variance threshold for foreground detection
    
    Returns:
        Tuple of (x_min, y_min, x_max, y_max)
    """
    # Compute variance in blocks
    block_size = 16
    h, w = image.shape
    
    foreground = np.zeros((h // block_size, w // block_size), dtype=bool)
    
    for i in range(0, h - block_size, block_size):
        for j in range(0, w - block_size, block_size):
            block = image[i:i+block_size, j:j+block_size]
            var = np.var(block)
            if var > threshold:
                foreground[i//block_size, j//block_size] = True
    
    # Find bounding box
    if not np.any(foreground):
        return 0, 0, w, h
    
    rows = np.any(foreground, axis=1)
    cols = np.any(foreground, axis=0)
    
    y_min = np.where(rows)[0][0] * block_size
    y_max = (np.where(rows)[0][-1] + 1) * block_size
    x_min = np.where(cols)[0][0] * block_size
    x_max = (np.where(cols)[0][-1] + 1) * block_size
    
    return x_min, y_min, x_max, y_max


def decode_wsq(wsq_data: Union[bytes, str, Path]) -> Tuple[npt.NDArray[np.uint8], int, bool]:
    """
    Decode a WSQ compressed fingerprint image.
    
    WSQ (Wavelet Scalar Quantization) is the FBI's standard compression format
    for fingerprint images. This function uses NBIS's WSQ decoder.
    
    Args:
        wsq_data: Either bytes containing WSQ data, or path to WSQ file
    
    Returns:
        Tuple of (image, ppi, lossy_flag):
            - image: Grayscale uint8 numpy array
            - ppi: Pixels per inch resolution
            - lossy_flag: Whether lossy compression was used
    
    Raises:
        RuntimeError: If NBIS extension is not available
        RuntimeError: If WSQ decoding fails
        FileNotFoundError: If file path provided but doesn't exist
    
    Example:
        >>> # From file
        >>> img, ppi, lossy = decode_wsq('fingerprint.wsq')
        >>> # From bytes
        >>> with open('fingerprint.wsq', 'rb') as f:
        >>>     img, ppi, lossy = decode_wsq(f.read())
    """
    try:
        from . import _nbis_ext
    except ImportError:
        raise RuntimeError("NBIS extension not available. Please build/install pynbis properly.")
    
    # If path provided, read file
    if isinstance(wsq_data, (str, Path)):
        filepath = Path(wsq_data)
        if not filepath.exists():
            raise FileNotFoundError(f"File not found: {filepath}")
        with open(filepath, 'rb') as f:
            wsq_data = f.read()
    
    if not isinstance(wsq_data, bytes):
        raise TypeError("wsq_data must be bytes or file path")
    
    # Decode using NBIS
    image, ppi, lossyflag = _nbis_ext.decode_wsq(wsq_data)
    
    return image, ppi, bool(lossyflag)

