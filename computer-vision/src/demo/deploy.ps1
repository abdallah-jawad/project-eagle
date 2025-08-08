# Planogram Vision Demo - Windows Deployment Script
# This script handles OpenCV compatibility issues in Windows environments

param(
    [string]$Mode = "run"
)

Write-Host "🚀 Starting Planogram Vision Demo Deployment..." -ForegroundColor Green

# Function to set up environment variables
function Setup-Environment {
    Write-Host "🔧 Setting up environment variables..." -ForegroundColor Yellow
    
    # Set OpenCV environment variables
    $env:DEBIAN_FRONTEND = "noninteractive"
    $env:DISPLAY = ":99"
    $env:OPENCV_VIDEOIO_PRIORITY_MSMF = "0"
    $env:OPENCV_VIDEOIO_DEBUG = "1"
    $env:OPENCV_LOG_LEVEL = "ERROR"
    
    # Application-specific environment variables
    $env:PLANOGRAM_CONFIG_DIR = if ($env:PLANOGRAM_CONFIG_DIR) { $env:PLANOGRAM_CONFIG_DIR } else { "config/planograms" }
    $env:PLANOGRAM_IMAGES_DIR = if ($env:PLANOGRAM_IMAGES_DIR) { $env:PLANOGRAM_IMAGES_DIR } else { "config/images" }
    $env:PLANOGRAM_WEIGHTS_DIR = if ($env:PLANOGRAM_WEIGHTS_DIR) { $env:PLANOGRAM_WEIGHTS_DIR } else { "weights" }
    $env:PLANOGRAM_TEMP_DIR = if ($env:PLANOGRAM_TEMP_DIR) { $env:PLANOGRAM_TEMP_DIR } else { "temp" }
    $env:PLANOGRAM_MODEL_WEIGHTS = if ($env:PLANOGRAM_MODEL_WEIGHTS) { $env:PLANOGRAM_MODEL_WEIGHTS } else { "pick-instance-seg-v11-1.2.pt" }
    
    Write-Host "✅ Environment variables configured" -ForegroundColor Green
}

# Function to install Python dependencies
function Install-PythonDeps {
    Write-Host "🐍 Installing Python dependencies..." -ForegroundColor Yellow
    
    # Upgrade pip
    python -m pip install --upgrade pip
    
    # Install requirements
    python -m pip install --no-cache-dir -r requirements.txt
    
    Write-Host "✅ Python dependencies installed successfully" -ForegroundColor Green
}

# Function to create necessary directories
function Create-Directories {
    Write-Host "📁 Creating necessary directories..." -ForegroundColor Yellow
    
    $directories = @(
        "config/planograms",
        "config/images", 
        "weights",
        "temp"
    )
    
    foreach ($dir in $directories) {
        if (!(Test-Path $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
            Write-Host "  Created: $dir" -ForegroundColor Cyan
        }
    }
    
    Write-Host "✅ Directories created successfully" -ForegroundColor Green
}

# Function to run the application
function Start-Application {
    Write-Host "🎯 Starting Streamlit application..." -ForegroundColor Yellow
    
    # Set Streamlit configuration
    $env:STREAMLIT_SERVER_PORT = "8501"
    $env:STREAMLIT_SERVER_ADDRESS = "0.0.0.0"
    $env:STREAMLIT_SERVER_HEADLESS = "true"
    $env:STREAMLIT_BROWSER_GATHER_USAGE_STATS = "false"
    
    # Run the application
    streamlit run app.py --server.port=8501 --server.address=0.0.0.0 --server.headless=true --browser.gatherUsageStats=false
}

# Function to check if model weights exist
function Test-ModelWeights {
    $weightsPath = Join-Path $env:PLANOGRAM_WEIGHTS_DIR $env:PLANOGRAM_MODEL_WEIGHTS
    if (!(Test-Path $weightsPath)) {
        Write-Host "⚠️  Warning: Model weights file not found at $weightsPath" -ForegroundColor Yellow
        Write-Host "   Please ensure your model weights are in the weights/ directory" -ForegroundColor Yellow
    } else {
        Write-Host "✅ Model weights found at $weightsPath" -ForegroundColor Green
    }
}

# Function to check OpenCV installation
function Test-OpenCVInstallation {
    Write-Host "🔍 Testing OpenCV installation..." -ForegroundColor Yellow
    
    try {
        python -c "import cv2; print(f'OpenCV version: {cv2.__version__}')"
        Write-Host "✅ OpenCV installed successfully" -ForegroundColor Green
    }
    catch {
        Write-Host "❌ OpenCV installation failed: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "💡 Try installing opencv-python-headless instead:" -ForegroundColor Cyan
        Write-Host "   pip uninstall opencv-python" -ForegroundColor Gray
        Write-Host "   pip install opencv-python-headless" -ForegroundColor Gray
        exit 1
    }
}

# Main deployment logic
function Start-Deployment {
    Write-Host "🔍 Starting deployment process..." -ForegroundColor Yellow
    
    # Set up environment
    Setup-Environment
    
    # Install Python dependencies
    Install-PythonDeps
    
    # Test OpenCV installation
    Test-OpenCVInstallation
    
    # Create directories
    Create-Directories
    
    # Check model weights
    Test-ModelWeights
    
    # Run the application
    Start-Application
}

# Handle different deployment modes
switch ($Mode.ToLower()) {
    "docker" {
        Write-Host "🐳 Docker deployment mode" -ForegroundColor Cyan
        Start-Deployment
    }
    "local" {
        Write-Host "💻 Local deployment mode" -ForegroundColor Cyan
        Start-Deployment
    }
    "python-deps" {
        Write-Host "🐍 Installing Python dependencies only" -ForegroundColor Cyan
        Install-PythonDeps
    }
    "setup" {
        Write-Host "🔧 Setup mode" -ForegroundColor Cyan
        Setup-Environment
        Create-Directories
    }
    "test-opencv" {
        Write-Host "🔍 Testing OpenCV installation" -ForegroundColor Cyan
        Test-OpenCVInstallation
    }
    "run" {
        Write-Host "🚀 Standard deployment mode" -ForegroundColor Cyan
        Start-Deployment
    }
    default {
        Write-Host "🚀 Standard deployment mode" -ForegroundColor Cyan
        Start-Deployment
    }
}
