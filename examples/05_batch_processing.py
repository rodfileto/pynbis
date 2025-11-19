
#!/usr/bin/env python3
"""
Example 5: Batch Processing

This example demonstrates how to process multiple fingerprints
in batch mode, extracting minutiae and computing quality scores.
"""

import numpy as np
from pathlib import Path
from typing import List, Dict
from pynbis import Fingerprint
import json

def process_fingerprint(image: np.ndarray, ppi: int = 500) -> Dict:
    """Process a single fingerprint and return results."""
    fp = Fingerprint(image, ppi=ppi)
    
    # Extract minutiae
    fp.extract_minutiae()
    
    # Compute quality
    fp.compute_quality()
    
    # Gather results
    results = {
        'minutiae_count': len(fp.minutiae),
        'quality_score': fp.quality.quality,
        'quality_confidence': fp.quality.confidence,
        'minutiae': [
            {
                'x': m.x,
                'y': m.y,
                'direction': m.direction,
                'type': m.minutia_type.name,
                'quality': m.quality,
            }
            for m in fp.minutiae
        ]
    }
    
    return results

def main():
    print("PyNBIS Example 5: Batch Processing")
    print("=" * 50)
    
    # Simulate a batch of fingerprints
    print("\nGenerating 20 sample fingerprints...")
    fingerprints = []
    for i in range(20):
        # In practice, you would load real images
        image = np.random.randint(0, 256, (480, 640), dtype=np.uint8)
        fingerprints.append((f"FP_{i+1:03d}", image))
    
    # Process all fingerprints
    print("\nProcessing fingerprints...")
    print("-" * 50)
    
    all_results = {}
    
    for fp_id, image in fingerprints:
        try:
            results = process_fingerprint(image)
            all_results[fp_id] = results
            
            # Print progress
            quality = results['quality_score']
            minutiae = results['minutiae_count']
            print(f"✓ {fp_id}: Quality={quality}/5, Minutiae={minutiae}")
            
        except Exception as e:
            print(f"✗ {fp_id}: Error - {str(e)}")
            all_results[fp_id] = {'error': str(e)}
    
    # Statistics
    print("\nBatch Statistics:")
    print("-" * 50)
    
    successful = [r for r in all_results.values() if 'error' not in r]
    
    if successful:
        qualities = [r['quality_score'] for r in successful]
        minutiae_counts = [r['minutiae_count'] for r in successful]
        
        print(f"Total processed: {len(all_results)}")
        print(f"Successful: {len(successful)}")
        print(f"Failed: {len(all_results) - len(successful)}")
        
        print(f"\nQuality Distribution:")
        for q in range(1, 6):
            count = qualities.count(q)
            percentage = (count / len(qualities)) * 100
            bar = "█" * int(percentage / 5)
            print(f"  Quality {q}: {count:2d} ({percentage:5.1f}%) {bar}")
        
        print(f"\nMinutiae Statistics:")
        print(f"  Average: {sum(minutiae_counts) / len(minutiae_counts):.1f}")
        print(f"  Minimum: {min(minutiae_counts)}")
        print(f"  Maximum: {max(minutiae_counts)}")
        
        # Quality-based filtering
        print(f"\nQuality Filtering (threshold <= 3):")
        high_quality = [fp_id for fp_id, r in all_results.items() 
                        if 'error' not in r and r['quality_score'] <= 3]
        print(f"  High quality prints: {len(high_quality)}/{len(successful)}")
        print(f"  Percentage: {(len(high_quality)/len(successful))*100:.1f}%")
        
        # Minutiae-based filtering
        print(f"\nMinutiae Filtering (threshold >= 25):")
        sufficient_minutiae = [fp_id for fp_id, r in all_results.items()
                              if 'error' not in r and r['minutiae_count'] >= 25]
        print(f"  Sufficient minutiae: {len(sufficient_minutiae)}/{len(successful)}")
        print(f"  Percentage: {(len(sufficient_minutiae)/len(successful))*100:.1f}%")
        
        # Combined filtering
        print(f"\nCombined Filtering (quality <= 3 AND minutiae >= 25):")
        good_prints = [fp_id for fp_id, r in all_results.items()
                      if 'error' not in r 
                      and r['quality_score'] <= 3 
                      and r['minutiae_count'] >= 25]
        print(f"  Good quality prints: {len(good_prints)}/{len(successful)}")
        print(f"  IDs: {', '.join(good_prints[:5])}..." if len(good_prints) > 5 
              else f"  IDs: {', '.join(good_prints)}")
    
    # Save results to JSON
    print(f"\nSaving results to batch_results.json...")
    
    # Convert numpy types to native Python types for JSON serialization
    json_results = {}
    for fp_id, result in all_results.items():
        if 'minutiae' in result:
            result['minutiae'] = [
                {k: float(v) if isinstance(v, (np.floating, np.integer)) else v 
                 for k, v in m.items()}
                for m in result['minutiae']
            ]
        json_results[fp_id] = result
    
    with open('batch_results.json', 'w') as f:
        json.dump(json_results, f, indent=2)
    
    print("✓ Results saved successfully")


if __name__ == "__main__":
    main()
