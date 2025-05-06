import os
import shutil
from pathlib import Path
import sys

def copy_dlls(src_dir, dst_dir, dlls):
    """Copy DLLs from source to destination directory."""
    for dll in dlls:
        src = src_dir / dll
        dst = dst_dir / dll
        if src.exists():
            print(f"Copying {dll}...")
            shutil.copy2(src, dst)
        else:
            print(f"Warning: {dll} not found in {src_dir}")

# Define paths
cuda_path = Path("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.9")
cuda_bin = cuda_path / "bin"
cudnn_path = Path("C:/Program Files/NVIDIA/CUDNN/v9.9/bin/12.9")
onnx_dir = Path(os.path.expanduser("~/AppData/Roaming/Python/Python313/site-packages/onnxruntime/capi"))

# Required CUDA DLLs
cuda_dlls = [
    "cublas64_12.dll",
    "cublasLt64_12.dll",
    "cudart64_12.dll",
    "cufft64_12.dll",
    "curand64_12.dll",
    "cusolver64_12.dll",
    "cusparse64_12.dll",
    "cudnn64_8.dll",
    "cudnn_adv_infer64_8.dll",
    "cudnn_adv_train64_8.dll",
    "cudnn_cnn_infer64_8.dll",
    "cudnn_cnn_train64_8.dll",
    "cudnn_ops_infer64_8.dll",
    "cudnn_ops_train64_8.dll",
    "cudnn_graph64_9.dll"
]

# Copy CUDA DLLs
print("Copying CUDA DLLs...")
copy_dlls(cuda_bin, onnx_dir, cuda_dlls)

# Copy cuDNN DLLs if they exist
if cudnn_path.exists():
    print("\nCopying cuDNN DLLs...")
    copy_dlls(cudnn_path, onnx_dir, cuda_dlls)

# Add CUDA paths to PATH
cuda_paths = [
    str(cuda_bin),
    str(cudnn_path),
    str(cuda_path / "extras/CUPTI/lib64")
]

# Update PATH environment variable
current_path = os.environ.get('PATH', '')
new_paths = [p for p in cuda_paths if p not in current_path]
if new_paths:
    os.environ['PATH'] = current_path + os.pathsep + os.pathsep.join(new_paths)
    print("\nAdded CUDA paths to environment:")
    for path in new_paths:
        print(f"  - {path}")

print("\nSetup complete! Please restart your Python environment and try running your code again.") 