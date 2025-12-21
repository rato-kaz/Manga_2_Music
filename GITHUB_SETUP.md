# 🚀 Hướng Dẫn Đưa Project Lên GitHub

## 📋 Bước 1: Chuẩn Bị

### 1.1 Kiểm tra Git Status

```bash
# Kiểm tra xem đã có git repo chưa
git status

# Nếu chưa có, khởi tạo
git init
```

### 1.2 Kiểm tra .gitignore

Đảm bảo `.gitignore` đã bao gồm:
- `__pycache__/`
- `.env`
- `venv/`
- `output/`
- `logs/`
- `*.wav`, `*.mp3`
- `models/`

## 📝 Bước 2: Tạo Repository trên GitHub

1. Đăng nhập vào [GitHub](https://github.com)
2. Click **"New repository"** (hoặc vào https://github.com/new)
3. Điền thông tin:
   - **Repository name**: `Manga_2_Music` (hoặc tên bạn muốn)
   - **Description**: "Manga-to-Music: Convert manga to audio experience"
   - **Visibility**: Public hoặc Private
   - **Không** check "Initialize with README" (vì đã có README)
4. Click **"Create repository"**

## 🔗 Bước 3: Kết Nối Local với GitHub

### 3.1 Thêm Remote

```bash
# Thay YOUR_USERNAME bằng GitHub username của bạn
git remote add origin https://github.com/YOUR_USERNAME/Manga_2_Music.git

# Hoặc dùng SSH (nếu đã setup SSH key)
git remote add origin git@github.com:YOUR_USERNAME/Manga_2_Music.git
```

### 3.2 Kiểm tra Remote

```bash
git remote -v
```

## 📤 Bước 4: Commit và Push

### 4.1 Stage Files

```bash
# Xem các file sẽ được commit
git status

# Thêm tất cả files (trừ những file trong .gitignore)
git add .

# Hoặc thêm từng file cụ thể
git add README.md
git add src/
git add requirements.txt
```

### 4.2 Commit

```bash
# Commit với message
git commit -m "feat: initial commit - Manga-to-Music project"

# Hoặc commit với message chi tiết hơn
git commit -m "feat: initial commit

- Add core pipeline modules
- Add API with FastAPI
- Add logging system
- Add Docker support
- Add documentation"
```

### 4.3 Push lên GitHub

```bash
# Push lên main branch
git branch -M main
git push -u origin main

# Nếu gặp lỗi authentication, có thể cần:
# - Setup GitHub Personal Access Token
# - Hoặc dùng GitHub CLI: gh auth login
```

## 🔐 Bước 5: Setup Authentication (Nếu Cần)

### Option 1: Personal Access Token

1. GitHub → Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Generate new token
3. Chọn scopes: `repo`
4. Copy token
5. Khi push, dùng token làm password

### Option 2: SSH Key

```bash
# Generate SSH key
ssh-keygen -t ed25519 -C "your_email@example.com"

# Copy public key
cat ~/.ssh/id_ed25519.pub

# Add vào GitHub: Settings → SSH and GPG keys → New SSH key
```

### Option 3: GitHub CLI

```bash
# Install GitHub CLI
# Windows: winget install GitHub.cli
# Mac: brew install gh
# Linux: apt install gh

# Login
gh auth login

# Clone và push sẽ tự động authenticate
```

## ✅ Bước 6: Verify

1. Vào repository trên GitHub
2. Kiểm tra các files đã được upload
3. Kiểm tra README hiển thị đúng
4. Test clone repository:
   ```bash
   cd /tmp
   git clone https://github.com/YOUR_USERNAME/Manga_2_Music.git
   ```

## 🎨 Bước 7: Tùy Chọn - Setup Repository

### 7.1 Thêm Topics/Tags

Vào repository → Settings → Topics, thêm:
- `python`
- `manga`
- `audio-generation`
- `deep-learning`
- `fastapi`
- `tts`

### 7.2 Thêm Description

Update repository description với:
```
🎵 Convert manga to immersive audio experience with BGM, SFX, and character voices
```

### 7.3 Setup GitHub Pages (Nếu Cần)

1. Settings → Pages
2. Source: Deploy from branch
3. Branch: `main` / `docs`

## 📊 Bước 8: Tùy Chọn - Badges và Links

Update README.md với badges (đã có sẵn):
- Python version
- License
- Code style

## 🔄 Bước 9: Workflow Tiếp Theo

### Thêm Changes

```bash
# 1. Make changes
# 2. Stage changes
git add .

# 3. Commit
git commit -m "feat: add new feature"

# 4. Push
git push
```

### Tạo Branch cho Feature

```bash
# Create và switch to new branch
git checkout -b feature/new-feature

# Make changes, commit
git add .
git commit -m "feat: add new feature"

# Push branch
git push -u origin feature/new-feature

# Create Pull Request trên GitHub
```

## 🐛 Troubleshooting

### Lỗi: "remote origin already exists"

```bash
# Xóa remote cũ
git remote remove origin

# Thêm lại
git remote add origin https://github.com/YOUR_USERNAME/Manga_2_Music.git
```

### Lỗi: "Authentication failed"

- Kiểm tra username/password
- Hoặc dùng Personal Access Token
- Hoặc setup SSH key

### Lỗi: "Large files"

Nếu có file lớn (>100MB), GitHub sẽ từ chối:
- Xóa file khỏi git: `git rm --cached large_file.pt`
- Thêm vào .gitignore
- Commit lại

## 📚 Resources

- [GitHub Docs](https://docs.github.com/)
- [Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [Conventional Commits](https://www.conventionalcommits.org/)

---

**Chúc bạn thành công! 🎉**

