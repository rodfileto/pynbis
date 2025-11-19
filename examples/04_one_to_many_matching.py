
#!/usr/bin/env python3
"""
Example 4: 1:N Identification (One-to-Many Matching)

This example demonstrates how to match a probe fingerprint
against a gallery of multiple fingerprints for identification.
"""

import numpy as np
from pynbis import Fingerprint

def main():
    print("PyNBIS Example 4: 1:N Identification")
    print("=" * 50)
    
    # Create probe fingerprint
    probe_image = np.random.randint(0, 256, (480, 640), dtype=np.uint8)
    probe = Fingerprint(probe_image, ppi=500)
    probe.extract_minutiae()
    
    print(f"Probe fingerprint: {len(probe.minutiae)} minutiae")
    
    # Create gallery of fingerprints
    print("\nCreating gallery of 10 fingerprints...")
    gallery = []
    for i in range(10):
        gallery_image = np.random.randint(0, 256, (480, 640), dtype=np.uint8)
        fp = Fingerprint(gallery_image, ppi=500)
        fp.extract_minutiae()
        gallery.append(fp)
        print(f"  Gallery #{i+1}: {len(fp.minutiae)} minutiae")
    
    # Perform 1:N matching
    print("\nMatching probe against gallery...")
    print("-" * 50)
    
    results = []
    for i, gallery_fp in enumerate(gallery):
        match_result = probe.match(gallery_fp)
        results.append((i + 1, match_result.score))
    
    # Sort by score (highest first)
    results.sort(key=lambda x: x[1], reverse=True)
    
    # Display results
    print("\nTop 5 matches:")
    print(f"{'Rank':<6} {'Gallery ID':<12} {'Score':<8} {'Confidence'}")
    print("-" * 50)
    
    for rank, (gallery_id, score) in enumerate(results[:5], 1):
        if score >= 100:
            confidence = "Very High"
        elif score >= 60:
            confidence = "High"
        elif score >= 40:
            confidence = "Medium"
        elif score >= 20:
            confidence = "Low"
        else:
            confidence = "Very Low"
        
        print(f"{rank:<6} Gallery #{gallery_id:<5} {score:<8} {confidence}")
    
    # Identification decision
    print("\nIdentification Decision:")
    print("-" * 50)
    
    threshold = 60  # Identification threshold
    best_match_id, best_score = results[0]
    
    if best_score >= threshold:
        print(f"✓ IDENTIFIED: Gallery #{best_match_id} (score: {best_score})")
    else:
        print(f"✗ NOT IDENTIFIED: Best score {best_score} below threshold {threshold}")
    
    # Show score distribution
    print("\nScore Distribution:")
    print("-" * 50)
    
    score_ranges = [
        (100, float('inf'), "Excellent (100+)"),
        (60, 100, "Good (60-99)"),
        (40, 60, "Moderate (40-59)"),
        (20, 40, "Weak (20-39)"),
        (0, 20, "No match (0-19)"),
    ]
    
    for min_score, max_score, label in score_ranges:
        count = sum(1 for _, score in results if min_score <= score < max_score)
        bar = "█" * count
        print(f"{label:<20} {count:2d} {bar}")


if __name__ == "__main__":
    main()
