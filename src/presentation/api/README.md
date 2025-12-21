# 🚀 Manga-to-Music API

FastAPI-based REST API for manga-to-audio conversion.

## 📋 Features

- ✅ Process single chapters
- ✅ Process entire volumes
- ✅ Async processing support
- ✅ Comprehensive error handling
- ✅ Automatic API documentation
- ✅ Request/Response validation
- ✅ Health check endpoints

## 🚀 Quick Start

### Run API Server

```bash
# Development mode
python -m src.presentation.api.app

# Or using uvicorn directly
uvicorn src.presentation.api.app:app --reload --host 0.0.0.0 --port 8000
```

### Access API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📚 API Endpoints

### Health Check

```http
GET /health
```

### Process Chapter

```http
POST /api/v1/processing/chapter
Content-Type: application/json

{
  "manga_name": "My_Manga",
  "chapter_number": 1,
  "image_paths": [
    "/path/to/page1.jpg",
    "/path/to/page2.jpg"
  ],
  "enable_bgm": true,
  "enable_tts": true,
  "device": "cuda"
}
```

### Process Volume

```http
POST /api/v1/processing/volume
Content-Type: application/json

{
  "manga_root": "/path/to/manga",
  "max_chapters": 5,
  "enable_bgm": true,
  "enable_tts": true,
  "device": "cuda"
}
```

## 🏗️ Architecture

```
src/presentation/api/
├── app.py              # FastAPI app instance
├── schemas.py          # Pydantic models
├── exceptions.py       # Custom exceptions
├── dependencies.py     # Dependency injection
└── routes/
    ├── health.py       # Health check routes
    └── processing.py   # Processing routes
```

## 🔧 Configuration

### CORS

Configure CORS origins in `app.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Your frontend
    ...
)
```

### Output Directory

Configure output directory in `dependencies.py`:

```python
def get_processing_service():
    output_dir = Path("/custom/output/path")
    service = MangaProcessingService(output_base_dir=output_dir)
    yield service
```

## 📝 Error Handling

All errors are handled consistently:

```json
{
  "error": "ValidationError",
  "message": "Image file not found: /path/to/image.jpg",
  "detail": {}
}
```

## 🧪 Testing

```bash
# Run tests
pytest tests/

# Test API endpoints
curl http://localhost:8000/health
```

## 📖 Examples

See `examples/` directory for API usage examples.

