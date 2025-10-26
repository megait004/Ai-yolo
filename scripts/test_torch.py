"""
Script test PyTorch
"""

import os
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

print("Testing PyTorch installation...")
print("=" * 50)

try:
    import torch
    print(f"✅ PyTorch version: {torch.__version__}")
    print(f"✅ CUDA available: {torch.cuda.is_available()}")
    cuda_version = getattr(torch.version, 'cuda', None) if torch.cuda.is_available() else None  # pyright: ignore[reportAttributeAccessIssue]
    print(f"✅ CUDA version: {cuda_version or 'N/A'}")
    print("=" * 50)
    print("✅ PyTorch is working!")
except Exception as e:
    print(f"❌ Error: {e}")
    print("=" * 50)
    print("PyTorch installation has issues!")

input("\nPress Enter to exit...")
