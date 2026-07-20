# Breast Cancer AI Analysis System

A comprehensive Django-based web application for breast cancer analysis using both traditional machine learning and deep learning approaches.

## Features

### 1. Image Analysis (ResNet50)
- **AI-Powered Histopathology Image Analysis**
- Upload breast cancer histopathology images
- Automatic classification: Benign (0) or Malignant (1)
- Cancer stage assessment based on confidence levels
- Support for multiple image formats (JPEG, PNG, BMP, TIFF)

### 2. Risk Assessment (ML Pipeline)
- **Patient Risk Assessment Tool**
- Input patient demographics and medical history
- Genetic factors and family history analysis
- Risk probability calculation
- Comprehensive risk scoring

### 3. Professional Dashboard
- **Clinician-Friendly Interface**
- Quick access to both analysis tools
- System status monitoring
- Model accuracy information
- Professional navigation system

### 4. Comprehensive Reporting System
- **Analytics Dashboard** with overview statistics
- **Risk Assessment Reports** with graphs and charts
- **Image Analysis Reports** with cancer stage distribution
- **Checkup History** - complete list of all assessments
- **PDF Export** functionality for all reports
- **Print-friendly** reports for documentation

### 5. User Management
- **User Guide** with comprehensive documentation
- **Logout** functionality for security
- **Professional navigation** system

## Installation

### Prerequisites
- Python 3.8 or higher
- Django 4.0 or higher

### Step 1: Install Dependencies

#### Quick Installation (Recommended)
```bash
# Install basic requirements
pip install -r requirements.txt

# Install PyTorch (choose one method below)
```

#### Method 1: Automatic Installation (Windows)
```bash
# Run the installation script
python install_pytorch.py

# OR double-click the batch file
install_pytorch.bat
```

#### Method 2: Manual Installation
```bash
# CPU version (recommended for most users):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu

# GPU version (if you have CUDA 11.8):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# GPU version (if you have CUDA 12.1):
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
```

#### Method 3: Using Conda
```bash
# If you prefer conda:
conda install pytorch torchvision cpuonly -c pytorch
```

### Step 2: Setup Django Project

```bash
# Navigate to project directory
cd breast_cancer

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

### Step 3: Access the Application

Open your browser and navigate to:
- **Main Dashboard**: http://127.0.0.1:8000/
- **Image Analysis**: http://127.0.0.1:8000/image-predict/
- **Risk Assessment**: http://127.0.0.1:8000/dashboard/

## Model Files Required

Ensure these model files are in the `breast_cancerapp/models/` directory:

1. **`breast_cancer_resnet50_full.pth`** - ResNet50 model for image classification
2. **`breast_cancer_pipeline.joblib`** - ML pipeline for risk assessment

## Usage Guide

### Image Analysis Workflow

1. **Access Image Analysis**
   - Navigate to "AI Analysis Tools" → "Image Analysis"
   - Or use the dashboard quick action button

2. **Upload Image**
   - Drag and drop or click to browse
   - Supported formats: JPEG, PNG, BMP, TIFF
   - Recommended: High-resolution histopathology images

3. **View Results**
   - Prediction: Benign or Malignant
   - Confidence level percentage
   - Cancer stage assessment (for malignant cases)
   - Detailed probability breakdown

### Risk Assessment Workflow

1. **Access Risk Assessment**
   - Navigate to "AI Analysis Tools" → "Risk Assessment"
   - Or use the dashboard quick action button

2. **Input Patient Data**
   - Fill in patient demographics
   - Medical history and genetic factors
   - Family history information

3. **View Risk Score**
   - Risk probability percentage
   - Detailed input summary
   - Confidence metrics

## Technical Details

### Image Analysis Model
- **Architecture**: ResNet50 (Deep Convolutional Neural Network)
- **Input**: 224x224 pixel RGB images
- **Output**: Binary classification (0=Benign, 1=Malignant)
- **Staging**: Confidence-based stage assessment
- **Accuracy**: 95.2% (validated on test dataset)

### Risk Assessment Model
- **Type**: Machine Learning Pipeline
- **Features**: Patient demographics, medical history, genetic factors
- **Output**: Risk probability score
- **Validation**: Clinical datasets

## File Structure

```
breast_cancer/
├── breast_cancer/          # Django project settings
├── breast_cancerapp/      # Main application
│   ├── models/            # Model files
│   ├── templates/         # HTML templates
│   ├── image_predictor.py # ResNet50 predictor
│   ├── views.py           # Django views
│   └── urls.py            # URL routing
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

## Important Notes

⚠️ **Medical Disclaimer**: This system is designed for clinical decision support only. All predictions should be reviewed and validated by qualified medical professionals before making any clinical decisions.

## Troubleshooting

### Common Issues

1. **PyTorch Error: "name 'torch' is not defined"**
   ```bash
   # This means PyTorch is not installed. Run one of these:
   
   # Quick fix (Windows):
   python install_pytorch.py
   
   # Manual fix:
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   
   # Verify installation:
   python -c "import torch; print('PyTorch version:', torch.__version__)"
   ```

2. **Model File Not Found**
   - Ensure `breast_cancer_resnet50_full.pth` is in `breast_cancerapp/models/`
   - Check file permissions
   - Verify the file path is correct

3. **CUDA/GPU Issues**
   ```bash
   # If you get CUDA errors, install CPU version:
   pip install torch torchvision --index-url https://download.pytorch.org/whl/cpu
   
   # To check if CUDA is available after installation:
   python -c "import torch; print('CUDA available:', torch.cuda.is_available())"
   ```

4. **Django Migration Issues**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Image Upload Issues**
   - Supported formats: JPEG, PNG, BMP, TIFF
   - Maximum file size: Check Django settings
   - Ensure image is a valid histopathology image

## Support

For technical support or questions about the system, please refer to the Django documentation or contact your system administrator.

## License

This project is intended for medical research and clinical decision support purposes.
