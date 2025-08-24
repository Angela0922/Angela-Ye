# 🎥 TikTok Video Translator & Makeup Transformer

A sophisticated AI-powered application that translates Spanish TikTok e-commerce videos to English while transforming Latino makeup styles to mainstream American beauty aesthetics.

## ✨ Features

### 🎤 Audio Translation
- **Speech Recognition**: Uses OpenAI Whisper to transcribe Spanish audio with high accuracy
- **AI Translation**: Leverages OpenAI GPT-3.5-turbo for natural, context-aware translation
- **E-commerce Optimization**: Specially tuned for TikTok e-commerce content and American social media culture
- **Text-to-Speech**: Generates natural-sounding English audio using Google Text-to-Speech

### 💄 Makeup Transformation
- **Face Detection**: Advanced MediaPipe face mesh detection with 468 facial landmarks
- **Skin Tone Adjustment**: Subtle lighting and color adjustments for mainstream American appearance
- **Eye Enhancement**: Enhances eye prominence with American makeup styling
- **Lip Color Application**: Applies natural pink lip colors popular in American beauty standards
- **Cheek Contouring**: Adds subtle cheek enhancement and contouring
- **Eyebrow Definition**: Defines eyebrows according to American beauty trends
- **Overall Brightness**: Adjusts facial brightness for a mainstream American look

### 🎬 Video Processing
- **Frame-by-Frame Processing**: Processes each video frame individually for consistent results
- **Audio Synchronization**: Maintains perfect sync between transformed video and translated audio
- **Quality Preservation**: Maintains original video quality while applying transformations
- **Multiple Formats**: Supports MP4, MOV, AVI video formats

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key (for translation)
- At least 4GB RAM (8GB recommended)
- GPU support recommended for faster processing

### Installation

1. **Clone the repository**:
```bash
git clone <repository-url>
cd tiktok-transformer
```

2. **Install dependencies**:
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**:
```bash
cp .env.example .env
# Edit .env and add your OpenAI API key
```

4. **Run the application**:
```bash
python app.py
```

5. **Open your browser** and navigate to `http://localhost:5000`

## 🔧 Configuration

### Environment Variables
```env
OPENAI_API_KEY=your_openai_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
UPLOAD_FOLDER=uploads
OUTPUT_FOLDER=outputs
MAX_CONTENT_LENGTH=104857600  # 100MB max file size
```

### Makeup Transformation Parameters
You can adjust the makeup transformation parameters in `makeup_transformer.py`:

```python
self.american_makeup_style = {
    'skin_tone_adjustment': 0.15,  # Skin lightening factor (0.0-1.0)
    'eye_enhancement': 1.3,        # Eye prominence multiplier
    'lip_color': (180, 100, 120),  # RGB values for lip color
    'cheek_enhancement': 1.2,      # Cheek enhancement factor
    'eyebrow_definition': 1.1,     # Eyebrow definition multiplier
    'overall_brightness': 1.1      # Overall brightness adjustment
}
```

## 📱 Usage

### Web Interface
1. **Upload Video**: Drag and drop or select a TikTok video file
2. **Monitor Progress**: Watch real-time processing progress with detailed status updates
3. **Download Result**: Download the transformed video with English audio and American makeup styling

### API Endpoints

#### Upload Video
```http
POST /upload
Content-Type: multipart/form-data

{
  "video": <video_file>
}
```

#### Check Processing Status
```http
GET /status/<job_id>
```

#### Download Processed Video
```http
GET /download/<job_id>
```

## 🏗️ Architecture

### Core Components

1. **Flask Web Application** (`app.py`)
   - Handles file uploads and downloads
   - Manages processing jobs and status tracking
   - Provides RESTful API endpoints

2. **Video Processor** (`video_processor.py`)
   - Extracts audio from video files
   - Converts frames to/from video format
   - Combines processed video with new audio

3. **Translation Service** (`translation_service.py`)
   - Transcribes Spanish audio using Whisper
   - Translates text using OpenAI GPT-3.5-turbo
   - Generates English TTS audio

4. **Makeup Transformer** (`makeup_transformer.py`)
   - Detects faces and facial landmarks
   - Applies American makeup styling transformations
   - Processes video frame-by-frame

### Processing Pipeline

1. **Audio Extraction**: Extract audio track from uploaded video
2. **Speech Recognition**: Transcribe Spanish audio to text
3. **Translation**: Convert Spanish text to English
4. **TTS Generation**: Create English audio from translated text
5. **Face Detection**: Identify faces in each video frame
6. **Makeup Transformation**: Apply American styling to detected faces
7. **Video Synthesis**: Combine transformed video with English audio

## 🎨 Makeup Transformation Details

### Facial Landmark Detection
Uses MediaPipe's 468-point face mesh for precise facial feature identification:
- Eyes: 32 landmarks per eye
- Lips: 40 landmarks
- Face contour: 17 landmarks
- Eyebrows: 10 landmarks per eyebrow

### Transformation Techniques
- **LAB Color Space**: For natural skin tone adjustments
- **Gaussian Blurring**: For smooth mask transitions
- **Alpha Blending**: For natural makeup application
- **Gradient Masks**: For realistic cheek contouring

## 🔒 Privacy & Ethics

This application is designed for:
- ✅ Content localization and cultural adaptation
- ✅ E-commerce marketing optimization
- ✅ Personal content creation

**Important Considerations**:
- Always obtain proper consent before processing videos of other people
- Respect cultural differences and avoid stereotyping
- Use responsibly for legitimate business and creative purposes
- Be mindful of the ethical implications of appearance modification

## 🛠️ Development

### Project Structure
```
tiktok-transformer/
├── app.py                    # Main Flask application
├── video_processor.py        # Video processing utilities
├── translation_service.py    # Translation and TTS services
├── makeup_transformer.py     # Makeup transformation engine
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── templates/
│   └── index.html           # Web interface
├── uploads/                 # Uploaded video files
├── outputs/                 # Processed video files
└── temp/                    # Temporary processing files
```

### Adding New Features

1. **Custom Makeup Styles**: Extend `MakeupTransformer` class with new styling methods
2. **Additional Languages**: Add support for other languages in `TranslationService`
3. **Video Effects**: Implement new video filters in `VideoProcessor`
4. **API Extensions**: Add new endpoints in `app.py`

## 🔧 Troubleshooting

### Common Issues

**OpenCV Installation Issues**:
```bash
pip install opencv-python-headless
```

**MediaPipe Installation Issues**:
```bash
pip install --upgrade pip
pip install mediapipe
```

**Memory Issues with Large Videos**:
- Reduce video resolution before processing
- Process videos in smaller chunks
- Increase available RAM or use GPU acceleration

**Audio Sync Issues**:
- Ensure consistent frame rates
- Check audio duration matching
- Verify TTS timing

### Performance Optimization

1. **GPU Acceleration**: Install CUDA-compatible PyTorch for faster processing
2. **Batch Processing**: Process multiple frames simultaneously
3. **Video Compression**: Use lower quality settings for faster processing
4. **Caching**: Cache face detection results for similar frames

## 📊 System Requirements

### Minimum Requirements
- CPU: Dual-core 2.0GHz+
- RAM: 4GB
- Storage: 2GB free space
- Python: 3.8+

### Recommended Requirements
- CPU: Quad-core 3.0GHz+
- RAM: 8GB+
- GPU: NVIDIA GTX 1060 or equivalent
- Storage: 10GB free space
- Python: 3.9+

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📞 Support

For technical support or questions:
- Create an issue on GitHub
- Check the troubleshooting section
- Review the documentation

---

**⚠️ Disclaimer**: This tool is intended for legitimate content creation and marketing purposes. Users are responsible for ensuring proper consent and ethical use of the transformation features.
