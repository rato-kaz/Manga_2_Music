# 📁 Refactor Plan: Tổ Chức Lại File Structure

## 🎯 Mục Tiêu

Sắp xếp lại các file theo Clean Architecture và best practices:
- Modules vào `src/` theo layers
- Documentation vào `docs/`
- Config files ở root
- Tests vào `tests/`

## 📋 Structure Mới

```
Manga_2_Music/
├── src/                          # Source code
│   ├── domain/                   # Domain layer
│   │   ├── entities.py
│   │   ├── exceptions.py
│   │   ├── constants.py
│   │   └── utils.py
│   │
│   ├── application/              # Application layer
│   │   └── use_cases/
│   │
│   ├── infrastructure/           # Infrastructure layer
│   │   ├── image/
│   │   │   └── image_loader.py
│   │   ├── models/              # Model wrappers
│   │   │   ├── magi_wrapper.py
│   │   │   ├── musicgen_wrapper.py
│   │   │   ├── audiogen_wrapper.py
│   │   │   └── tts_wrapper.py
│   │   └── exceptions.py
│   │
│   ├── presentation/            # Presentation layer
│   │   └── cli/
│   │
│   └── core/                    # Core modules (legacy, sẽ migrate)
│       ├── visual_analysis/
│       │   ├── reading_order.py
│       │   ├── character_reid.py
│       │   ├── speaker_diarization.py
│       │   ├── manpu_detector.py
│       │   └── onomatopoeia_classifier.py
│       ├── semantic/
│       │   ├── semantic_extractor.py
│       │   └── timeline_generator.py
│       ├── audio/
│       │   ├── audio_generator.py
│       │   └── audio_mixer.py
│       ├── tts/
│       │   └── tts_engine.py
│       └── pipeline/
│           ├── pipeline_base.py
│           ├── pipeline_enhanced.py
│           └── full_pipeline.py
│
├── tests/                       # Tests
│   ├── unit/
│   ├── integration/
│   └── e2e/
│
├── docs/                        # Documentation
│   ├── README.md
│   ├── implementation/
│   │   ├── README_IMPLEMENTATION.md
│   │   ├── IMPLEMENTATION_SUMMARY.md
│   │   └── FINAL_IMPLEMENTATION_SUMMARY.md
│   ├── planning/
│   │   ├── Kế Hoạch Phát Triển Dự Án Manga-to-Music.md
│   │   └── ROADMAP_NEXT_STEPS.md
│   └── clean_code/
│       ├── CLEAN_CODE_REFACTOR.md
│       └── CLEAN_CODE_CHECKLIST.md
│
├── config/                      # Configuration
│   └── settings.py
│
├── scripts/                     # Utility scripts
│
├── .github/                     # GitHub workflows
│   └── workflows/
│
├── data/                        # Data files (gitignored)
│
├── output/                      # Output files (gitignored)
│
├── requirements.txt             # Dependencies
├── requirements-dev.txt         # Dev dependencies
├── pyproject.toml              # Project config
├── .pylintrc                   # Linter config
├── .gitignore                  # Git ignore
├── Makefile                    # Build commands
└── README.md                   # Main README (link to docs/)
```

## 🔄 Migration Steps

1. Tạo folder structure mới
2. Di chuyển files vào đúng vị trí
3. Update imports trong các files
4. Update documentation paths
5. Test để đảm bảo không break

