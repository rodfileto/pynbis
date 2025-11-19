
"""
Basic tests for PyNBIS core functionality.
"""

import pytest
import numpy as np


def test_import():
    """Test that the package can be imported."""
    import pynbis
    assert pynbis.__version__ is not None


def test_minutia_class():
    """Test Minutia dataclass."""
    from pynbis import Minutia, MinutiaType
    
    m = Minutia(
        x=100,
        y=200,
        direction=90,
        minutia_type=MinutiaType.RIDGE_ENDING,
        quality=0.95
    )
    
    assert m.x == 100
    assert m.y == 200
    assert m.direction == 90
    assert m.minutia_type == MinutiaType.RIDGE_ENDING
    assert m.quality == 0.95


def test_fingerprint_class():
    """Test Fingerprint class initialization."""
    from pynbis import Fingerprint
    
    image = np.random.randint(0, 256, (480, 640), dtype=np.uint8)
    fp = Fingerprint(image, ppi=500)
    
    assert fp.image is not None
    assert fp.ppi == 500
    assert fp.minutiae is None
    assert fp.quality is None


def test_match_result():
    """Test MatchResult dataclass."""
    from pynbis import MatchResult
    
    result = MatchResult(score=75, matched=True)
    assert result.score == 75
    assert result.matched is True


def test_quality_result():
    """Test QualityResult dataclass."""
    from pynbis import QualityResult
    
    quality = QualityResult(quality=2, confidence=0.85, return_code=0)
    assert quality.quality == 2
    assert quality.confidence == 0.85
    assert 1 <= quality.quality <= 5


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
