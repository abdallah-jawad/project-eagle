# Planogram Vision Demo - Deployment Guide

This guide covers how to deploy the Planogram Vision Demo as a Streamlit application in various environments.

## Prerequisites

- Python 3.8 or higher
- Required Python packages (see requirements.txt)
- Model weights file (pick-instance-seg-v11-1.2.pt)
- Sample planogram configuration files and images

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Set up configuration directories:**
   ```bash
   mkdir -p config/planograms config/images weights
   ```

3. **Place your model weights:**
   - Copy `pick-instance-seg-v11-1.2.pt` to the `weights/` directory

4. **Add sample configurations:**
   - Place planogram JSON configurations in `config/planograms/`
   - Place planogram images in `config/images/`

5. **Run the application:**
   ```bash
   streamlit run app.py
   ```

## Environment Configuration

The application supports environment variables for flexible deployment configuration:

### Directory Paths
- `PLANOGRAM_CONFIG_DIR`: Directory for planogram configuration files (default: `config/planograms`)
- `PLANOGRAM_IMAGES_DIR`: Directory for planogram images (default: `config/images`)
- `PLANOGRAM_WEIGHTS_DIR`: Directory for model weights (default: `weights`)
- `PLANOGRAM_TEMP_DIR`: Temporary files directory (default: `/tmp` on Unix, `~/temp` on Windows)

### Model Configuration
- `PLANOGRAM_MODEL_WEIGHTS`: Model weights filename (default: `pick-instance-seg-v11-1.2.pt`)

### Example .env file
```bash
# Copy .env.example to .env and modify as needed
PLANOGRAM_CONFIG_DIR=/app/data/configs
PLANOGRAM_IMAGES_DIR=/app/data/images
PLANOGRAM_WEIGHTS_DIR=/app/models
PLANOGRAM_TEMP_DIR=/tmp/planogram
PLANOGRAM_MODEL_WEIGHTS=pick-instance-seg-v11-1.2.pt
```

## Deployment Options

### 1. Local Development
```bash
streamlit run app.py
```

### 2. Docker Deployment
Create a Dockerfile:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py"]
```

### 3. Cloud Deployment (Streamlit Cloud, Heroku, etc.)
- Set environment variables in your cloud platform
- Ensure model weights and sample data are included in your deployment
- Configure appropriate file paths for your deployment environment

### 4. Production Deployment
For production deployments:
1. Set `STREAMLIT_ENABLE_CORS=false`
2. Set `STREAMLIT_ENABLE_XSRF_PROTECTION=false` (if needed)
3. Use proper SSL certificates
4. Configure appropriate resource limits
5. Set up monitoring and logging

## File Structure

```
demo/
├── app.py                          # Main Streamlit application
├── requirements.txt                # Python dependencies
├── .streamlit/config.toml         # Streamlit configuration
├── .env.example                   # Environment variables example
├── DEPLOYMENT.md                  # This file
├── backend/                       # Backend modules
│   ├── config.py                  # Configuration management
│   ├── inference.py               # Model inference
│   ├── planogram_analyzer.py      # Main analysis logic
│   ├── planogram_annotator.py     # Image annotation
│   ├── streamlit_drawer.py        # Drawing interface
│   └── ...
├── config/                        # Configuration files
│   ├── planograms/               # Planogram configurations
│   └── images/                   # Planogram images
└── weights/                       # Model weights
    └── pick-instance-seg-v11-1.2.pt
```

## Troubleshooting

### Common Issues

1. **Model weights not found:**
   - Ensure the weights file is in the correct directory
   - Check `PLANOGRAM_WEIGHTS_DIR` and `PLANOGRAM_MODEL_WEIGHTS` environment variables

2. **Configuration files not loading:**
   - Verify `PLANOGRAM_CONFIG_DIR` points to the correct directory
   - Ensure JSON configuration files are valid

3. **Font loading errors:**
   - The application will fallback to default fonts if system fonts are not available
   - This is normal in containerized environments

4. **Temporary file permissions:**
   - Ensure the `PLANOGRAM_TEMP_DIR` is writable
   - Check file system permissions

### Performance Optimization

1. **Memory usage:**
   - Consider image size limits for large planogram images
   - Monitor memory usage during inference

2. **Model loading:**
   - Model is loaded once at startup for better performance
   - Consider model optimization for production use

## Security Considerations

1. **File uploads:**
   - Validate uploaded file types and sizes
   - Consider virus scanning for production deployments

2. **Configuration:**
   - Protect configuration directories in production
   - Use secure file permissions

3. **Network:**
   - Use HTTPS in production
   - Configure proper firewall rules