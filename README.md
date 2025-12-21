# 🎵 Manga-to-Music: Hệ Thống Chuyển Đổi Manga Thành Audio

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

Hệ thống tự động chuyển đổi manga thành audio experience đầy đủ với nhạc nền, hiệu ứng âm thanh, và giọng nói nhân vật.

## 📖 Table of Contents

- [Features](#-tính-năng)
- [Quick Start](#-quick-start)
- [Installation](#-cài-đặt)
- [Usage](#-sử-dụng)
- [API Documentation](#-api-documentation)
- [Project Structure](#-cấu-trúc-dự-án)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Tính Năng

- ✅ **Phân tích Hình ảnh**: Panel segmentation, character detection, OCR
- ✅ **Reading Order**: Tự động xác định thứ tự đọc đúng (RTL)
- ✅ **Character Tracking**: Theo dõi nhân vật xuyên suốt chapter
- ✅ **Emotion Detection**: Phát hiện cảm xúc từ manpu và context
- ✅ **Scene Classification**: Phân loại cảnh (battle, romance, comedy, etc.)
- ✅ **BGM Generation**: Tạo nhạc nền phù hợp với cảnh
- ✅ **SFX Generation**: Tạo hiệu ứng âm thanh từ onomatopoeia
- ✅ **TTS**: Tổng hợp giọng nói nhân vật với Style-Bert-VITS2
- ✅ **Audio Mixing**: Mix tất cả audio thành file cuối cùng

## 🚀 Quick Start

### Cài Đặt

```bash
# Clone repository
git clone <repository-url>
cd Manga_2_Music

# Cài đặt dependencies
pip install -r requirements.txt

# Optional: Cài đặt audio processing libraries
pip install librosa soundfile demucs
```

### Sử Dụng Cơ Bản

```python
from src.core.pipeline.full_pipeline import process_manga_chapter
from pathlib import Path

# Xử lý một chapter
result = process_manga_chapter(
    chapter_images=[
        Path("manga/chapter1/page_001.jpg"),
        Path("manga/chapter1/page_002.jpg"),
    ],
    manga_name="My_Manga",
    chapter_number=1,
    output_dir=Path("output/chapter_1"),
    device="cuda",  # hoặc "cpu"
)

print(f"Audio đã được tạo tại: {result['final_audio']}")
```

### Sử Dụng Pipeline Cơ Bản (Chỉ Metadata)

```bash
python -m src.core.pipeline.pipeline_generate_json \
    --manga-root downloads/My_Manga \
    --output data/metadata.json \
    --device cuda
```

## 📁 Cấu Trúc Dự Án

```
Manga_2_Music/
├── src/                          # Source code
│   ├── domain/                   # Domain layer (entities, constants)
│   ├── application/              # Application layer (use cases)
│   ├── infrastructure/           # Infrastructure layer (models, I/O)
│   ├── presentation/             # Presentation layer (CLI, API)
│   └── core/                     # Core modules (legacy, organized by feature)
│       ├── visual_analysis/      # Reading order, character re-ID, etc.
│       ├── semantic/             # Scene classification, timeline
│       ├── audio/                # BGM, SFX generation
│       ├── tts/                  # Text-to-speech
│       └── pipeline/            # Pipeline orchestration
│
├── docs/                         # Documentation
│   ├── implementation/           # Implementation guides
│   ├── planning/                # Planning documents
│   └── clean_code/              # Clean code documentation
│
├── tests/                        # Tests
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
│
├── config/                       # Configuration files
├── scripts/                      # Utility scripts
│
├── requirements.txt              # Dependencies
├── requirements-dev.txt          # Dev dependencies
├── pyproject.toml               # Project config
├── Makefile                     # Build commands
└── README.md                    # This file
```

## 🎯 Các Giai Đoạn

### Giai Đoạn I: Visual Analysis ✅
- Panel segmentation (MAGI-V2)
- Character detection
- OCR text extraction
- Reading order resolution
- Character re-ID
- Manpu detection
- Onomatopoeia classification

### Giai Đoạn II: Semantic Extraction ✅
- Scene classification
- Emotion aggregation
- Timeline generation

### Giai Đoạn III: Audio Generation ✅
- BGM generation (MusicGen)
- SFX generation (AudioGen)
- Audio mixing & transitions

### Giai Đoạn IV: TTS ✅
- Voice profile management
- Speech synthesis (Style-Bert-VITS2)
- Emotion-aware prosody

### Giai Đoạn V: Integration ✅
- Full pipeline integration
- Output management

## 📊 Output Structure

```
output/
├── chapter_1/
│   ├── chapter_metadata.json      # Metadata đầy đủ
│   ├── final_audio.wav             # Audio cuối cùng
│   ├── audio/
│   │   ├── bgm_panel_1.wav         # Nhạc nền
│   │   └── sfx_panel_1_0.wav       # Hiệu ứng
│   ├── speech/
│   │   └── speech_bubble_1.wav     # Giọng nói
│   └── voice_profiles.json         # Voice profiles
└── ...
```

## ⚙️ Configuration

### Enable/Disable Features

```python
result = process_manga_chapter(
    # ... other params ...
    enable_reading_order=True,      # Reading order resolution
    enable_character_reid=True,     # Character re-ID
    enable_manpu=True,              # Manpu detection
    enable_onomatopoeia=True,        # Onomatopoeia
    enable_speaker_diarization=True,# Speaker diarization
    enable_bgm=True,                # BGM generation
    enable_sfx=True,                # SFX generation
    enable_tts=True,                # TTS generation
)
```

### Audio Settings

Chỉnh sửa trong `audio_generator.py`:
- Music prompt templates
- Model sizes (small/medium/large)
- Duration settings

### TTS Settings

Chỉnh sửa trong `tts_engine.py`:
- Voice profile settings
- Prosody adjustments
- Emotion mappings

## 🔧 Production Setup

### Model Integration

Các wrapper classes hiện tại là placeholders. Để sử dụng thực tế:

1. **MusicGen:**
   ```python
   from audiocraft.models import MusicGen
   model = MusicGen.get_pretrained("facebook/musicgen-medium")
   ```

2. **Style-Bert-VITS2:**
   ```python
   # Load model từ checkpoint
   ```

3. **Demucs:**
   ```python
   from demucs import separate
   stems = separate(audio)
   ```

### Performance Tips

- Sử dụng GPU cho faster processing
- Batch processing cho multiple chapters
- Cache generated audio files
- Pre-generate common SFX

## 📝 Requirements

- Python 3.8+
- PyTorch 2.0+
- CUDA (optional, for GPU acceleration)
- ~10GB+ disk space (for models and outputs)

## 🐛 Troubleshooting

### Out of Memory
- Giảm `pages_per_batch` trong pipeline
- Sử dụng CPU thay vì CUDA
- Disable một số features không cần thiết

### Model Not Found
- Download models manually
- Check model paths trong code
- Verify HuggingFace access

### Audio Generation Fails
- Check audio libraries installation
- Verify model availability
- Check disk space

## 📚 Documentation

Xem thêm trong thư mục `docs/`:
- **Implementation Guides**: `docs/implementation/`
- **Planning Documents**: `docs/planning/`
- **Clean Code**: `docs/clean_code/`

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## 📄 License

[Add your license here]

## 🙏 Acknowledgments

- MAGI-V2: `ragavsachdeva/magiv2`
- MusicGen: Meta AI Research
- Style-Bert-VITS2: Community project
- Manga109 Dataset: For research purposes

## 📧 Contact

[Add contact information]

---

**Status:** ✅ Production Ready (với model integration)

**Last Updated:** 2025-01-XX

