
#!/usr/bin/env python3
"""
Example 2: Fingerprint Matching (1:1 Comparison)

This example demonstrates how to match two fingerprint images
and interpret the matching scores.
"""

import numpy as np
from pathlib import Path
from pynbis import match_fingerprints, Fingerprint

try:
    from imageio.v2 import imread
    from scipy.ndimage import rotate
    HAS_IMAGEIO = True
    HAS_SCIPY = True
except ImportError:
    HAS_IMAGEIO = False
    HAS_SCIPY = False

def interpret_score(score):
    """Interpret a match score and return a description."""
    if score >= 100:
        return "Excellent match (very high confidence)"
    elif score >= 60:
        return "Good match (high confidence)"
    elif score >= 40:
        return "Moderate match (medium confidence)"
    elif score >= 20:
        return "Weak match (low confidence)"
    else:
        return "No match (very low confidence)"

def load_sample_images():
    """Load real fingerprint images if available, else generate random."""
    # Try to load from data/fingerprints first (high quality)
    fingerprints_dir = Path(__file__).parent.parent / "data" / "fingerprints"
    
    if HAS_IMAGEIO and fingerprints_dir.exists():
        image_files = list(fingerprints_dir.glob("*.jpg")) + list(fingerprints_dir.glob("*.png"))
        if len(image_files) >= 1:
            try:
                # Load one image
                probe = imread(image_files[0]).astype(np.uint8)
                # Ensure grayscale
                if probe.ndim == 3:
                    probe = probe[:, :, 0]
                
                # Create rotated version as gallery (10 degrees)
                if HAS_SCIPY:
                    gallery = rotate(probe, angle=10, reshape=False, order=1, mode='constant', cval=255).astype(np.uint8)
                    print(f"Loaded real fingerprint from {fingerprints_dir.name}")
                    print(f"  Image: {image_files[0].name}")
                    print(f"  Gallery: Same image rotated 10°\n")
                else:
                    # Fallback to same image without rotation
                    gallery = probe.copy()
                    print(f"Loaded real fingerprint from {fingerprints_dir.name}")
                    print(f"  Image: {image_files[0].name}")
                    print(f"  Note: Install scipy for rotation test\n")
                
                return probe, gallery, True
            except Exception:
                pass
    
    # Fallback to SOCOFing dataset
    socofing_dir = Path(__file__).parent.parent / "data" / "socofing"
    if HAS_IMAGEIO and socofing_dir.exists():
        image_files = sorted(socofing_dir.glob("**/*.BMP"))
        if len(image_files) >= 1:
            try:
                probe = imread(image_files[0]).astype(np.uint8)
                if probe.ndim == 3:
                    probe = probe[:, :, 0]
                
                if HAS_SCIPY:
                    gallery = rotate(probe, angle=10, reshape=False, order=1, mode='constant', cval=255).astype(np.uint8)
                    print(f"Loaded fingerprint from SOCOFing dataset")
                    print(f"  Image: {image_files[0].name}")
                    print(f"  Gallery: Same image rotated 10°\n")
                else:
                    gallery = probe.copy()
                    print(f"Loaded fingerprint from SOCOFing dataset")
                    print(f"  Image: {image_files[0].name}\n")
                
                return probe, gallery, True
            except Exception:
                pass
    
    # Fallback to random images
    print("Using random images (install 'imageio' and run 'python scripts/download_socofing.py' for real data)")
    probe = np.random.randint(0, 256, (480, 640), dtype=np.uint8)
    gallery = np.random.randint(0, 256, (480, 640), dtype=np.uint8)
    return probe, gallery, False


def main():
    print("PyNBIS Example 2: Fingerprint Matching")
    print("=" * 50)
    
    # Scenario A: Two different images
    probe_image, gallery_image, using_real = load_sample_images()
    
    # Method 1: Functional API
    print("\n1. Using Functional API:")
    print("-" * 50)
    
    # Match without threshold (get score only)
    result = match_fingerprints(probe_image, gallery_image)
    print(f"Match score: {result.score}")
    print(f"Interpretation: {interpret_score(result.score)}")
    
    # Match with threshold (binary decision)
    result_with_threshold = match_fingerprints(
        probe_image, 
        gallery_image, 
        threshold=40
    )
    print(f"\nWith threshold=40:")
    print(f"  Score: {result_with_threshold.score}")
    print(f"  Matched: {result_with_threshold.matched}")
    
    # Method 2: Object-Oriented API
    print("\n2. Using Object-Oriented API:")
    print("-" * 50)
    
    probe = Fingerprint(probe_image, ppi=500)
    gallery = Fingerprint(gallery_image, ppi=500)
    
    # Extract minutiae first
    probe.extract_minutiae()
    gallery.extract_minutiae()
    
    print(f"Probe minutiae: {len(probe.minutiae)}")
    print(f"Gallery minutiae: {len(gallery.minutiae)}")
    
    # Match fingerprints
    result = probe.match(gallery, threshold=40)
    
    print(f"\nMatch result:")
    print(f"  Score: {result.score}")
    print(f"  Matched: {result.matched}")
    print(f"  Interpretation: {interpret_score(result.score)}")
    
    # Test multiple thresholds
    print("\n3. Testing Multiple Thresholds:")
    print("-" * 50)
    
    thresholds = [20, 40, 60, 80, 100]
    for threshold in thresholds:
        result = probe.match(gallery, threshold=threshold)
        match_str = "✓ MATCH" if result.matched else "✗ NO MATCH"
        print(f"Threshold {threshold:3d}: Score {result.score:3d} -> {match_str}")

    # Scenario B: Latent Match Simulation (partial fingerprint)
    print("\n4. Latent Match Simulation (partial fingerprints):")
    print("-" * 50)
    print("Simulating latent fingerprint matching by using half of the full image")
    
    h, w = probe_image.shape
    
    # Create partial latent images (like partial prints found at crime scenes)
    latent_vertical = probe_image[:, :w//2]  # Left half (vertical split)
    latent_horizontal = probe_image[:h//2, :]  # Top half (horizontal split)
    
    print(f"\nOriginal full print: {probe_image.shape}")
    print(f"Latent (vertical half): {latent_vertical.shape}")
    print(f"Latent (horizontal half): {latent_horizontal.shape}")
    
    # Match latent vertical against full print
    fp_full = Fingerprint(probe_image, ppi=500)
    fp_latent_v = Fingerprint(latent_vertical, ppi=500)
    fp_latent_h = Fingerprint(latent_horizontal, ppi=500)
    
    fp_full.extract_minutiae()
    fp_latent_v.extract_minutiae()
    fp_latent_h.extract_minutiae()
    
    print(f"\nMinutiae counts:")
    print(f"  Full print: {len(fp_full.minutiae)}")
    print(f"  Latent (vertical): {len(fp_latent_v.minutiae)}")
    print(f"  Latent (horizontal): {len(fp_latent_h.minutiae)}")
    
    result_v = fp_latent_v.match(fp_full, threshold=20)
    result_h = fp_latent_h.match(fp_full, threshold=20)
    
    print(f"\nLatent matching results:")
    print(f"  Vertical half vs Full: Score={result_v.score}, Matched={result_v.matched}")
    print(f"    {interpret_score(result_v.score)}")
    print(f"  Horizontal half vs Full: Score={result_h.score}, Matched={result_h.matched}")
    print(f"    {interpret_score(result_h.score)}")

    # Scenario C: Self-match (same image for probe and gallery)
    print("\n5. Self-Match Sanity Check (identical images):")
    print("-" * 50)

    # Functional API
    self_result = match_fingerprints(probe_image, probe_image)
    print(f"Self-match score (functional): {self_result.score}")
    print(f"Interpretation: {interpret_score(self_result.score)}")

    # OO API
    fp_same_a = Fingerprint(probe_image, ppi=500)
    fp_same_b = Fingerprint(probe_image, ppi=500)
    fp_same_a.extract_minutiae()
    fp_same_b.extract_minutiae()
    self_oo = fp_same_a.match(fp_same_b, threshold=40)
    print(f"Self-match (OO) -> Score: {self_oo.score}, Matched: {self_oo.matched}")


if __name__ == "__main__":
    main()
