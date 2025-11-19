
"""
Core functionality for PyNBIS fingerprint processing.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Tuple, Union
import numpy as np
import numpy.typing as npt

try:
    from . import _nbis_ext
except ImportError:
    # Fallback for development/testing
    _nbis_ext = None


class MinutiaType(Enum):
    """Minutia type enumeration."""
    RIDGE_ENDING = 0
    BIFURCATION = 1
    UNKNOWN = -1


@dataclass
class Minutia:
    """
    Represents a fingerprint minutia point.
    
    Attributes:
        x: X-coordinate in pixels
        y: Y-coordinate in pixels
        direction: Direction/angle (0-359 degrees or NBIS internal format)
        minutia_type: Type of minutia (ending or bifurcation)
        quality: Quality/reliability score (0.0-1.0)
    """
    x: int
    y: int
    direction: int
    minutia_type: MinutiaType
    quality: float = 1.0
    
    def to_dict(self) -> dict:
        """Convert minutia to dictionary format."""
        return {
            'x': self.x,
            'y': self.y,
            'direction': self.direction,
            'type': self.minutia_type.value,
            'quality': self.quality
        }


@dataclass
class MatchResult:
    """
    Result of a fingerprint matching operation.
    
    Attributes:
        score: Match score (higher indicates better match)
        probe_minutiae: Number of minutiae in probe
        gallery_minutiae: Number of minutiae in gallery
        matched: Whether prints match (if threshold applied)
    """
    score: int
    probe_minutiae: Optional[int] = None
    gallery_minutiae: Optional[int] = None
    matched: Optional[bool] = None
    
    def __str__(self) -> str:
        return f"MatchResult(score={self.score}, matched={self.matched})"


@dataclass
class QualityResult:
    """
    Result of fingerprint quality assessment (NFIQ).
    
    Attributes:
        quality: NFIQ quality value (1-5, where 1 is best)
        confidence: Confidence value
        return_code: Return code from NFIQ computation
    """
    quality: int
    confidence: float
    return_code: int
    
    def __str__(self) -> str:
        quality_desc = ["Excellent", "Very Good", "Good", "Fair", "Poor"]
        desc = quality_desc[self.quality - 1] if 1 <= self.quality <= 5 else "Unknown"
        return f"Quality: {self.quality}/5 ({desc}), Confidence: {self.confidence:.3f}"


class Fingerprint:
    """
    Object-oriented interface for fingerprint processing.
    
    Attributes:
        image: Grayscale fingerprint image (numpy array)
        ppi: Pixels per inch (default: 500)
        minutiae: Extracted minutiae (None until extract_minutiae is called)
        quality: Quality assessment (None until compute_quality is called)
    """
    
    def __init__(self, 
                 image: npt.NDArray[np.uint8], 
                 ppi: int = 500):
        """
        Initialize a Fingerprint object.
        
        Args:
            image: Grayscale fingerprint image (2D numpy array, uint8)
            ppi: Pixels per inch (default: 500)
        
        Raises:
            ValueError: If image format is invalid
        """
        if not isinstance(image, np.ndarray):
            raise ValueError("Image must be a numpy array")
        
        if image.dtype != np.uint8:
            raise ValueError("Image must be uint8 dtype")
        
        if image.ndim not in [2, 3]:
            raise ValueError("Image must be 2D or 3D array")
        
        # Convert to 2D if needed
        if image.ndim == 3:
            if image.shape[2] == 1:
                image = image[:, :, 0]
            else:
                raise ValueError("Color images not supported, use grayscale")
        
        self.image = image
        self.ppi = ppi
        self.minutiae: Optional[List[Minutia]] = None
        self.quality: Optional[QualityResult] = None
        self._binarized: Optional[npt.NDArray[np.uint8]] = None
    
    def extract_minutiae(self) -> List[Minutia]:
        """
        Extract minutiae from the fingerprint image.
        
        Returns:
            List of Minutia objects
        
        Raises:
            RuntimeError: If minutiae extraction fails
        """
        if _nbis_ext is None:
            raise RuntimeError("NBIS extension not available")
        
        result = _nbis_ext.extract_minutiae(self.image, self.ppi)
        
        self.minutiae = []
        for m_dict in result['minutiae']:
            minutia_type = MinutiaType.BIFURCATION if m_dict['type'] == 1 else MinutiaType.RIDGE_ENDING
            self.minutiae.append(Minutia(
                x=m_dict['x'],
                y=m_dict['y'],
                direction=m_dict['direction'],
                minutia_type=minutia_type,
                quality=m_dict['quality']
            ))
        
        self._binarized = result['binarized']
        return self.minutiae
    
    def compute_quality(self) -> QualityResult:
        """
        Compute NFIQ quality score for the fingerprint.
        
        Returns:
            QualityResult object
        
        Raises:
            RuntimeError: If quality computation fails
        """
        if _nbis_ext is None:
            raise RuntimeError("NBIS extension not available")
        
        result = _nbis_ext.compute_nfiq(self.image, self.ppi)
        self.quality = QualityResult(
            quality=result['quality'],
            confidence=result['confidence'],
            return_code=result['return_code']
        )
        return self.quality
    
    def match(self, other: 'Fingerprint', threshold: Optional[int] = None) -> MatchResult:
        """
        Match this fingerprint against another.
        
        Args:
            other: Another Fingerprint object
            threshold: Optional threshold for binary match decision
        
        Returns:
            MatchResult object
        
        Raises:
            RuntimeError: If matching fails
        """
        if _nbis_ext is None:
            raise RuntimeError("NBIS extension not available")
        
        score = _nbis_ext.match_fingerprints(self.image, other.image)
        
        matched = None
        if threshold is not None:
            matched = score >= threshold
        
        return MatchResult(
            score=score,
            probe_minutiae=len(self.minutiae) if self.minutiae else None,
            gallery_minutiae=len(other.minutiae) if other.minutiae else None,
            matched=matched
        )
    
    @property
    def binarized_image(self) -> Optional[npt.NDArray[np.uint8]]:
        """Get the binarized fingerprint image (if minutiae have been extracted)."""
        return self._binarized
    
    def __repr__(self) -> str:
        shape_str = f"{self.image.shape[0]}x{self.image.shape[1]}"
        min_str = f", {len(self.minutiae)} minutiae" if self.minutiae else ""
        qual_str = f", quality={self.quality.quality}" if self.quality else ""
        return f"Fingerprint({shape_str}{min_str}{qual_str})"


# Functional API

def extract_minutiae(image: npt.NDArray[np.uint8], 
                    ppi: int = 500) -> Tuple[List[Minutia], npt.NDArray[np.uint8]]:
    """
    Extract minutiae from a fingerprint image (functional interface).
    
    Args:
        image: Grayscale fingerprint image (2D numpy array, uint8)
        ppi: Pixels per inch (default: 500)
    
    Returns:
        Tuple of (minutiae_list, binarized_image)
    
    Raises:
        ValueError: If image format is invalid
        RuntimeError: If minutiae extraction fails
    
    Example:
        >>> import numpy as np
        >>> from pynbis import extract_minutiae
        >>> image = np.load('fingerprint.npy')
        >>> minutiae, binarized = extract_minutiae(image)
        >>> print(f"Found {len(minutiae)} minutiae")
    """
    fp = Fingerprint(image, ppi)
    minutiae = fp.extract_minutiae()
    return minutiae, fp.binarized_image


def match_fingerprints(probe: npt.NDArray[np.uint8], 
                      gallery: npt.NDArray[np.uint8],
                      threshold: Optional[int] = None,
                      ppi: int = 500) -> MatchResult:
    """
    Match two fingerprint images (functional interface).
    
    Args:
        probe: Probe fingerprint image
        gallery: Gallery fingerprint image
        threshold: Optional threshold for binary match decision
        ppi: Pixels per inch (default: 500)
    
    Returns:
        MatchResult object
    
    Raises:
        RuntimeError: If matching fails
    
    Example:
        >>> import numpy as np
        >>> from pynbis import match_fingerprints
        >>> probe = np.load('probe.npy')
        >>> gallery = np.load('gallery.npy')
        >>> result = match_fingerprints(probe, gallery)
        >>> print(f"Match score: {result.score}")
    """
    probe_fp = Fingerprint(probe, ppi)
    gallery_fp = Fingerprint(gallery, ppi)
    return probe_fp.match(gallery_fp, threshold)


def compute_quality(image: npt.NDArray[np.uint8], 
                   ppi: int = 500) -> QualityResult:
    """
    Compute NFIQ quality score for a fingerprint (functional interface).
    
    Args:
        image: Grayscale fingerprint image (2D numpy array, uint8)
        ppi: Pixels per inch (default: 500)
    
    Returns:
        QualityResult object
    
    Raises:
        RuntimeError: If quality computation fails
    
    Example:
        >>> import numpy as np
        >>> from pynbis import compute_quality
        >>> image = np.load('fingerprint.npy')
        >>> quality = compute_quality(image)
        >>> print(quality)
        Quality: 2/5 (Very Good), Confidence: 0.847
    """
    fp = Fingerprint(image, ppi)
    return fp.compute_quality()


def match_minutiae(probe_minutiae: List[Minutia], 
                  gallery_minutiae: List[Minutia]) -> MatchResult:
    """
    Match two sets of pre-extracted minutiae.
    
    Args:
        probe_minutiae: List of Minutia objects from probe
        gallery_minutiae: List of Minutia objects from gallery
    
    Returns:
        MatchResult object
    
    Raises:
        RuntimeError: If matching fails
    
    Example:
        >>> from pynbis import extract_minutiae, match_minutiae
        >>> probe_min, _ = extract_minutiae(probe_image)
        >>> gallery_min, _ = extract_minutiae(gallery_image)
        >>> result = match_minutiae(probe_min, gallery_min)
        >>> print(f"Match score: {result.score}")
    """
    if _nbis_ext is None:
        raise RuntimeError("NBIS extension not available")
    
    probe_list = [m.to_dict() for m in probe_minutiae]
    gallery_list = [m.to_dict() for m in gallery_minutiae]
    
    score = _nbis_ext.match_xyt(probe_list, gallery_list)
    
    return MatchResult(
        score=score,
        probe_minutiae=len(probe_minutiae),
        gallery_minutiae=len(gallery_minutiae)
    )
