#!/bin/bash

# TikTok Video Translator & Makeup Transformer Setup Script
# This script automates the installation and setup process

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -eq 0 ]]; then
   print_error "This script should not be run as root"
   exit 1
fi

# Print banner
echo -e "${BLUE}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║     TikTok Video Translator & Makeup Transformer Setup      ║"
echo "║                                                              ║"
echo "║  This script will install all dependencies and set up the   ║"
echo "║  application for you.                                        ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

# Check system requirements
print_status "Checking system requirements..."

# Check Python version
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version | cut -d' ' -f2 | cut -d'.' -f1,2)
    if [[ $(echo "$PYTHON_VERSION >= 3.8" | bc -l) -eq 1 ]]; then
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3.8 or higher is required. Found: $PYTHON_VERSION"
        exit 1
    fi
else
    print_error "Python 3 is not installed"
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    print_error "pip3 is not installed"
    exit 1
fi

# Check available disk space (at least 2GB)
AVAILABLE_SPACE=$(df . | awk 'NR==2 {print $4}')
if [[ $AVAILABLE_SPACE -lt 2097152 ]]; then  # 2GB in KB
    print_warning "Less than 2GB of disk space available. Installation may fail."
fi

# Check available RAM (at least 4GB)
if command -v free &> /dev/null; then
    AVAILABLE_RAM=$(free -m | awk 'NR==2{print $7}')
    if [[ $AVAILABLE_RAM -lt 4096 ]]; then
        print_warning "Less than 4GB of RAM available. Performance may be slow."
    fi
fi

# Create virtual environment
print_status "Creating Python virtual environment..."
if [[ ! -d "venv" ]]; then
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_warning "Virtual environment already exists"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install Python dependencies
print_status "Installing Python dependencies..."
if [[ -f "requirements.txt" ]]; then
    pip install -r requirements.txt
    print_success "Python dependencies installed"
else
    print_error "requirements.txt not found"
    exit 1
fi

# Install system dependencies (Ubuntu/Debian)
if command -v apt-get &> /dev/null; then
    print_status "Installing system dependencies..."
    sudo apt-get update
    sudo apt-get install -y \
        ffmpeg \
        libsm6 \
        libxext6 \
        libxrender-dev \
        libgomp1 \
        libglib2.0-0 \
        libgl1-mesa-glx \
        libgtk-3-0 \
        libavcodec-dev \
        libavformat-dev \
        libswscale-dev \
        libv4l-dev \
        libxvidcore-dev \
        libx264-dev \
        libjpeg-dev \
        libpng-dev \
        libtiff-dev \
        libatlas-base-dev \
        gfortran \
        wget \
        curl
    print_success "System dependencies installed"
elif command -v yum &> /dev/null; then
    print_status "Installing system dependencies (CentOS/RHEL)..."
    sudo yum update -y
    sudo yum install -y \
        ffmpeg \
        mesa-libGL \
        mesa-libGL-devel \
        libXext \
        libXrender \
        libXrender-devel \
        gcc \
        gcc-c++ \
        wget \
        curl
    print_success "System dependencies installed"
else
    print_warning "Could not detect package manager. Please install ffmpeg manually."
fi

# Create necessary directories
print_status "Creating application directories..."
mkdir -p models data output temp_frames temp_audio
print_success "Directories created"

# Download models
print_status "Downloading AI models..."
if [[ -f "download_models.py" ]]; then
    python download_models.py
    print_success "Models downloaded"
else
    print_warning "download_models.py not found. Models will be downloaded on first run."
fi

# Run tests
print_status "Running tests..."
if [[ -f "test_app.py" ]]; then
    python test_app.py
    if [[ $? -eq 0 ]]; then
        print_success "All tests passed"
    else
        print_warning "Some tests failed. Check the logs for details."
    fi
else
    print_warning "test_app.py not found. Skipping tests."
fi

# Set up Docker (optional)
if command -v docker &> /dev/null; then
    print_status "Docker detected. Building Docker image..."
    if [[ -f "Dockerfile" ]]; then
        docker build -t tiktok-transformer .
        print_success "Docker image built successfully"
        
        if [[ -f "docker-compose.yml" ]]; then
            print_status "Docker Compose configuration available"
            print_status "To run with Docker Compose: docker-compose up -d"
        fi
    fi
else
    print_warning "Docker not found. Skipping Docker setup."
fi

# Create startup script
print_status "Creating startup script..."
cat > start_app.sh << 'EOF'
#!/bin/bash
# Startup script for TikTok Video Translator & Makeup Transformer

# Activate virtual environment
source venv/bin/activate

# Check if running in Docker
if [[ -f /.dockerenv ]]; then
    echo "Running in Docker container..."
    streamlit run app.py --server.port=8501 --server.address=0.0.0.0
else
    echo "Running locally..."
    streamlit run app.py
fi
EOF

chmod +x start_app.sh
print_success "Startup script created"

# Print completion message
echo -e "${GREEN}"
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                    Setup Complete!                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo -e "${NC}"

print_success "Installation completed successfully!"
echo ""
print_status "To start the application:"
echo "  • Web interface: ./start_app.sh"
echo "  • Command line: python main.py --input video.mp4"
echo "  • Docker: docker-compose up -d"
echo ""
print_status "The web interface will be available at: http://localhost:8501"
echo ""
print_status "For more information, see the README.md file."

# Optional: Start the application
read -p "Would you like to start the application now? (y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    print_status "Starting application..."
    ./start_app.sh
fi