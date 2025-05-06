import os
import shutil
import sys
from pathlib import Path

def copy_dlls(src_dir, dst_dir, dlls):
    """Copy DLLs from source to destination directory."""
    for dll in dlls:
        src = src_dir / dll
        dst = dst_dir / dll
        if src.exists():
            print(f"Copying {dll}...")
            try:
                shutil.copy2(src, dst)
                print(f"Successfully copied {dll} to {dst}")
            except Exception as e:
                print(f"Error copying {dll}: {str(e)}")
        else:
            print(f"Warning: {dll} not found in {src_dir}")

# Define paths
cuda_path = Path("C:/Program Files/NVIDIA GPU Computing Toolkit/CUDA/v12.9")
cuda_bin = cuda_path / "bin"
cudnn_path = Path("C:/Program Files/NVIDIA/CUDNN/v9.9/bin/12.9")
onnx_dir = Path(os.path.expanduser("~/AppData/Roaming/Python/Python313/site-packages/onnxruntime/capi"))
python_dir = Path(os.path.expanduser("~/AppData/Roaming/Python/Python313"))
system32 = Path("C:/Windows/System32")

# Required DLLs
cuda_dlls = [
    "cublas64_12.dll",
    "cublasLt64_12.dll",
    "cudart64_12.dll",
    "cufft64_12.dll",
    "curand64_12.dll",
    "cusolver64_12.dll",
    "cusparse64_12.dll"
]

cudnn_dlls = [
    "cudnn64_9.dll",
    "cudnn_adv64_9.dll",
    "cudnn_cnn64_9.dll",
    "cudnn_engines_precompiled64_9.dll",
    "cudnn_engines_runtime_compiled64_9.dll",
    "cudnn_graph64_9.dll"
]

# Create directories if they don't exist
onnx_dir.mkdir(parents=True, exist_ok=True)
python_dir.mkdir(parents=True, exist_ok=True)

# Copy CUDA DLLs to all locations
print("Copying CUDA DLLs...")
copy_dlls(cuda_bin, onnx_dir, cuda_dlls)
copy_dlls(cuda_bin, python_dir, cuda_dlls)
copy_dlls(cuda_bin, system32, cuda_dlls)

# Copy cuDNN DLLs to all locations
print("\nCopying cuDNN DLLs...")
copy_dlls(cudnn_path, onnx_dir, cudnn_dlls)
copy_dlls(cudnn_path, python_dir, cudnn_dlls)
copy_dlls(cudnn_path, system32, cudnn_dlls)

# Add CUDA paths to PATH
cuda_paths = [
    str(cuda_bin),
    str(cudnn_path),
    str(cuda_path / "extras/CUPTI/lib64"),
    str(onnx_dir),
    str(python_dir)
]

# Update PATH environment variable
current_path = os.environ.get('PATH', '')
new_paths = [p for p in cuda_paths if p not in current_path]
if new_paths:
    os.environ['PATH'] = current_path + os.pathsep + os.pathsep.join(new_paths)
    print("\nAdded CUDA paths to environment:")
    for path in new_paths:
        print(f"  - {path}")

# Print current PATH for verification
print("\nCurrent PATH environment variable:")
for path in os.environ['PATH'].split(os.pathsep):
    print(f"  - {path}")

print("\nSetup complete! Please restart your Python environment and try running your code again.") 