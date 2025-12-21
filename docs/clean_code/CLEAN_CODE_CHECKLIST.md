# ✅ Clean Code Checklist - Manga-to-Music Project

## 📋 Tổng Quan

Dự án đã được refactor theo Clean Code principles. Document này liệt kê các tiêu chí và trạng thái implementation.

---

## 1️⃣ Principles

### ✅ Naming (Đặt tên rõ ràng)
- [x] Classes: PascalCase (`PageImage`, `BoundingBox`)
- [x] Functions: snake_case (`load_image`, `calculate_overlap`)
- [x] Constants: UPPER_SNAKE_CASE (`MIN_GUTTER_SIZE`, `WORDS_PER_MINUTE`)
- [x] Private methods: `_private_method`
- [x] Tên mô tả đúng mục đích, không viết tắt không rõ ràng

**Ví dụ:**
```python
# ✅ Good
def calculate_bbox_overlap(bbox1: BoundingBox, bbox2: BoundingBox) -> float:
    """Calculate overlap area between two bounding boxes."""

# ❌ Bad
def calc_overlap(b1, b2):
    pass
```

### ✅ Functions (Hàm ngắn, làm một việc)
- [x] Mỗi function làm một việc duy nhất
- [x] Functions ngắn (< 50 lines, tốt nhất < 20 lines)
- [x] Single Responsibility Principle
- [x] Pure functions khi có thể (không side effects)

**Ví dụ:**
```python
# ✅ Good - Single responsibility
def calculate_bbox_overlap(bbox1: BoundingBox, bbox2: BoundingBox) -> float:
    """Calculate overlap area."""
    # Only calculates overlap, no side effects

# ❌ Bad - Multiple responsibilities
def process_panel_and_save(panel, output_path):
    # Processes panel AND saves file - two responsibilities
```

### ✅ DRY (Don't Repeat Yourself)
- [x] Tách common logic thành utility functions
- [x] Constants centralized trong `domain/constants.py`
- [x] Base classes cho shared behavior
- [x] Helper functions trong `domain/utils.py`

**Ví dụ:**
```python
# ✅ Good - Reusable utility
def calculate_bbox_overlap(bbox1: BoundingBox, bbox2: BoundingBox) -> float:
    # Used in multiple places

# ❌ Bad - Duplicated code
# Same overlap calculation in 5 different files
```

### ✅ Readability (Code dễ đọc)
- [x] Code tự giải thích (self-documenting)
- [x] Logical flow rõ ràng
- [x] Avoid deep nesting (< 3 levels)
- [x] Early returns để giảm nesting

**Ví dụ:**
```python
# ✅ Good - Early return
def load_image(path: Path) -> PageImage:
    if not path.exists():
        raise InvalidImageError(f"File not found: {path}")
    # Continue processing...

# ❌ Bad - Deep nesting
def load_image(path: Path) -> PageImage:
    if path.exists():
        if path.suffix in SUPPORTED_FORMATS:
            # ... nested logic
```

### ✅ Comments (Giải thích lý do)
- [x] Docstrings cho public APIs
- [x] Comments giải thích "why", không phải "what"
- [x] Type hints thay vì comments về types
- [x] TODO comments với context

**Ví dụ:**
```python
# ✅ Good - Explains why
# Using LANCZOS resampling for better quality with manga images
resized = image.resize((w, h), Image.LANCZOS)

# ❌ Bad - Explains what (obvious)
# Resize the image
resized = image.resize((w, h))
```

### ✅ Layers (Tách logic theo layer)
- [x] Domain layer: Core business logic
- [x] Application layer: Use cases
- [x] Infrastructure layer: External dependencies
- [x] Presentation layer: Interfaces

**Structure:**
```
src/
├── domain/          # Business logic
├── application/      # Use cases
├── infrastructure/  # External deps
└── presentation/    # Interfaces
```

### ✅ Error Handling (Xử lý lỗi rõ ràng)
- [x] Custom exceptions cho domain errors
- [x] Clear error messages với context
- [x] Proper exception chaining
- [x] Error handling ở đúng layer

**Ví dụ:**
```python
# ✅ Good - Custom exception with context
class InvalidImageError(DomainException):
    pass

try:
    image = load_image(path)
except FileNotFoundError as e:
    raise InvalidImageError(f"Image file not found: {path}") from e
```

### ⚠️ Tests (Viết test)
- [ ] Unit tests cho domain logic
- [ ] Integration tests
- [ ] E2E tests
- [ ] Test coverage > 80%

**Status:** ⚠️ Cần implement

---

## 2️⃣ Process

### ✅ Coding Convention
- [x] PEP 8 compliance
- [x] Type hints (PEP 484)
- [x] Docstring conventions (Google style)
- [x] Line length: 100 characters

### ✅ Formatter & Linter
- [x] Black formatter configured (`pyproject.toml`)
- [x] isort for imports (`pyproject.toml`)
- [x] Pylint configured (`.pylintrc`)
- [x] MyPy for type checking (`pyproject.toml`)

**Usage:**
```bash
make format    # Format code
make lint      # Run linters
```

### ⚠️ Code Review
- [ ] Review checklist
- [ ] PR template
- [ ] Review guidelines

**Status:** ⚠️ Cần setup

### ✅ Git Workflow
- [x] `.gitignore` configured
- [x] Branch naming: `feature/xxx`, `refactor/xxx`, `bugfix/xxx`
- [x] Conventional Commits format

**Commit Format:**
```
feat: add reading order resolution
fix: correct bbox overlap calculation
refactor: extract image loading to service
docs: update README
test: add unit tests for domain utils
```

---

## 3️⃣ Architecture

### ✅ SOLID Principles

#### Single Responsibility Principle (S)
- [x] Mỗi class một trách nhiệm
- [x] `BoundingBox`: Chỉ quản lý bbox data
- [x] `ImageLoader`: Chỉ load images
- [x] `PageImage`: Chỉ represent page image

#### Open/Closed Principle (O)
- [x] Open for extension, closed for modification
- [x] Base classes cho extension
- [x] Interfaces cho abstraction

#### Liskov Substitution Principle (L)
- [x] Subtypes thay thế được base types
- [x] Proper inheritance hierarchy

#### Interface Segregation Principle (I)
- [x] Small, focused interfaces
- [x] Không force implementations

#### Dependency Inversion Principle (D)
- [x] Depend on abstractions
- [x] Dependency injection ready

### ✅ Clean Architecture
- [x] Domain layer độc lập
- [x] Dependencies point inward
- [x] Infrastructure implements domain interfaces
- [x] Clear separation of concerns

**Dependency Flow:**
```
Presentation → Application → Domain ← Infrastructure
```

### ✅ Folder Organization
- [x] Organized by layer/module
- [x] Clear module boundaries
- [x] `__init__.py` files
- [x] Related files grouped together

**Structure:**
```
src/
├── domain/              # Core business logic
│   ├── entities.py     # Domain entities
│   ├── exceptions.py   # Domain exceptions
│   ├── constants.py    # Domain constants
│   └── utils.py        # Domain utilities
│
├── application/         # Use cases
│   └── (use cases)
│
├── infrastructure/      # External deps
│   ├── image_loader.py
│   └── (model wrappers)
│
└── presentation/        # Interfaces
    └── (CLI, API)
```

---

## 📊 Implementation Status

### ✅ Completed
1. ✅ Domain layer structure
2. ✅ Domain entities với value objects
3. ✅ Custom exceptions
4. ✅ Constants centralization
5. ✅ Infrastructure layer structure
6. ✅ Image loader với error handling
7. ✅ Domain utilities
8. ✅ Code formatting setup
9. ✅ Linting setup
10. ✅ Git workflow

### ⚠️ In Progress
1. ⚠️ Application layer use cases
2. ⚠️ Infrastructure model wrappers
3. ⚠️ Tests

### 📝 TODO
1. [ ] Complete application layer
2. [ ] Refactor existing modules to use domain entities
3. [ ] Add comprehensive tests
4. [ ] Setup CI/CD
5. [ ] Documentation

---

## 🎯 Next Steps

1. **Refactor Existing Modules**
   - Migrate `reading_order.py` to use `BoundingBox`
   - Migrate `character_reid.py` to use domain entities
   - Update all modules to use domain layer

2. **Complete Application Layer**
   - Extract use cases from `full_pipeline.py`
   - Create application services
   - Define DTOs

3. **Add Tests**
   - Unit tests for domain
   - Integration tests
   - E2E tests

4. **Documentation**
   - API documentation
   - Architecture diagrams
   - Usage examples

---

## 📚 References

- Clean Code by Robert C. Martin
- Clean Architecture by Robert C. Martin
- PEP 8 - Style Guide for Python Code
- PEP 484 - Type Hints
- SOLID Principles

---

**Last Updated:** 2025-01-XX

**Status:** ✅ Foundation Complete | ⚠️ Migration In Progress

