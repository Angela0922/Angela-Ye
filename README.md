# TikTok Video Translator & Makeup Transformer

An AI-powered application that translates TikTok e-commerce videos from Spanish to English while transforming Latino makeup styles to American mainstream makeup looks.

## Features

- **Video Processing**: Extract and process TikTok video frames
- **Audio Translation**: Translate Spanish audio to English using Google Translate
- **Face Detection**: Identify faces in video frames using MediaPipe
- **Makeup Transformation**: Apply AI-powered makeup style transfer from Latino to American mainstream looks
- **Video Reconstruction**: Combine translated audio with transformed visuals
- **Web Interface**: User-friendly Streamlit interface for easy video upload and processing

## Installation

1. Clone this repository
2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Download required models:
```bash
python download_models.py
```

## Usage

### Web Interface
```bash
streamlit run app.py
```

### Command Line
```bash
python main.py --input video.mp4 --output translated_video.mp4
```

## Architecture

- **VideoProcessor**: Handles video frame extraction and reconstruction
- **AudioTranslator**: Manages audio extraction, translation, and synthesis
- **MakeupTransformer**: Applies AI makeup style transformation
- **FaceDetector**: Detects and tracks faces in video frames
- **VideoReconstructor**: Combines all components for final output

## Requirements

- Python 3.8+
- CUDA-compatible GPU (recommended for faster processing)
- 8GB+ RAM
- FFmpeg installed on system

## License

MIT License
