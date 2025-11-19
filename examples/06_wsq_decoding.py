#!/usr/bin/env python
"""
PyNBIS Example 6: WSQ Decoding

Demonstrates how to decode WSQ (Wavelet Scalar Quantization) compressed
fingerprint images, which is the FBI standard format for fingerprint storage.

WSQ files are commonly used in:
- NIST Special Database 4 (SD4)
- FBI fingerprint databases
- Many government biometric systems

To obtain WSQ test files:
- NIST SD4: https://www.nist.gov/srd/nist-special-database-4
- FVC datasets: http://bias.csr.unibo.it/fvc2000/
"""

from pynbis import decode_wsq, Fingerprint
from pathlib import Path


def main():
    print("PyNBIS Example 6: WSQ Decoding")
    print("=" * 50)
    
    # Look for WSQ files
    wsq_dir = Path(__file__).parent.parent / "data" / "wsq_samples"
    wsq_files = list(wsq_dir.glob("*.wsq")) if wsq_dir.exists() else []
    
    if not wsq_files:
        print("\nNo WSQ files found in data/wsq_samples/")
        print("\nTo test WSQ decoding:")
        print("1. Download NIST SD4 from: https://www.nist.gov/srd/nist-special-database-4")
        print("2. Place .wsq files in: data/wsq_samples/")
        print("3. Run this example again")
        print("\nShowing API usage with placeholder:")
        print()
        print("Code example:")
        print("-" * 50)
        print("""
# Decode from file
image, ppi, lossy = decode_wsq('fingerprint.wsq')
print(f"Image shape: {image.shape}")
print(f"Resolution: {ppi} ppi")
print(f"Lossy compression: {lossy}")

# Extract minutiae
fp = Fingerprint(image, ppi=ppi)
fp.extract_minutiae()
print(f"Found {len(fp.minutiae)} minutiae")

# Decode from bytes
with open('fingerprint.wsq', 'rb') as f:
    wsq_data = f.read()
    image, ppi, lossy = decode_wsq(wsq_data)
""")
        return
    
    # Process first WSQ file
    wsq_file = wsq_files[0]
    print(f"\n1. Decoding WSQ file:")
    print(f"   {wsq_file.name}")
    print("-" * 50)
    
    try:
        # Decode WSQ file
        image, ppi, lossy = decode_wsq(wsq_file)
        
        print(f"✓ Successfully decoded")
        print(f"  Image shape: {image.shape}")
        print(f"  Resolution: {ppi} ppi")
        print(f"  Lossy compression: {lossy}")
        print(f"  Data type: {image.dtype}")
        print(f"  Value range: {image.min()}-{image.max()}")
        
        # Extract minutiae from decoded image
        print(f"\n2. Extracting minutiae from decoded image:")
        print("-" * 50)
        
        fp = Fingerprint(image, ppi=ppi)
        fp.extract_minutiae()
        
        print(f"✓ Found {len(fp.minutiae)} minutiae")
        
        # Show first few minutiae
        print(f"\nFirst 5 minutiae:")
        for i, m in enumerate(fp.minutiae[:5]):
            print(f"  {i+1}. pos=({m.x:3d},{m.y:3d}), dir={m.direction:3d}°, "
                  f"type={m.minutia_type.name}, quality={m.quality:.2f}")
        
        # Compute quality
        quality_result = fp.compute_quality()
        print(f"\n3. NFIQ Quality Assessment:")
        print("-" * 50)
        print(f"  Quality: {quality_result.quality} (1=best, 5=worst)")
        print(f"  Return code: {quality_result.return_code}")
        
    except Exception as e:
        print(f"✗ Error: {e}")
        print("\nThis may indicate:")
        print("- Invalid or corrupted WSQ file")
        print("- Non-WSQ file with .wsq extension")
        print("- Unsupported WSQ variant")


if __name__ == "__main__":
    main()
