# Complete LaTeX Project Setup for TeXstudio + Windows 11

## ✅ XeLaTeX Configuration (REQUIRED)

Your project uses `\usepackage{fontspec}`, which **requires XeLaTeX** (not pdfLaTeX).
All build scripts have been updated to use XeLaTeX.

## 📁 Updated Directory Structure

Your LaTeX project now has this improved structure:
```
LaTeX/
├── build.bat                    # Main build script
├── submission/                  # Submission files (generated)
├── tools/                       # Build scripts and utilities
│   ├── build.bat               # Detailed build script
│   ├── build.sh                # Unix version
│   └── Makefile                # Make version
├── .gitignore                  # Git ignore file
└── High_Throughput_MLD.../     # Your manuscript
    ├── main.tex
    ├── mymanuscript.cls
    ├── sections/
    ├── Figures/
    └── bibliography/
```

## 🛠️ TeXstudio Setup Steps

### 1. Open Your Project
1. Launch TeXstudio
2. **File → Open** → Select `main.tex`
3. **File → Load Session** → Select `Paper2_Materials.txss`

### 2. Configure Build System
Go to **Options → Configure TeXstudio → Build**:

- **Default Compiler:** XeLaTeX ⚠️ (NOT pdfLaTeX)
- **Default Bibliography:** Biber
- **PDF Viewer:** Internal PDF Viewer

### 3. Add Custom User Commands
In **Build → User Commands**, add:

**Clean Build:**
```
cmd /c cd /d "%DIR%" && del *.aux *.bbl *.bcf *.blg *.log *.out *.run.xml *.synctex.gz
```

**Full Build:**
```
xelatex.exe -synctex=1 -interaction=nonstopmode %.tex | biber % | xelatex.exe -synctex=1 -interaction=nonstopmode %.tex | xelatex.exe -synctex=1 -interaction=nonstopmode %.tex
```

**Submission Package:**
```
cmd /c "%DIR%\..\build.bat" submission
```

### 4. Set Keyboard Shortcuts
In **Shortcuts** tab:
- **Build & View:** F5
- **User:Clean:Build:** Ctrl+Shift+C
- **User:Full:Build:** Ctrl+Shift+B

### 5. Editor Settings
In **Editor** tab:
- **Font:** Consolas, 12pt
- **Show Line Numbers:** ✅
- **Tab Width:** 4 spaces

## 🚀 Usage Instructions

### Daily Editing:
1. Open TeXstudio (loads your session automatically)
2. Edit your .tex files
3. Press **F5** to build and view

### Build Options:
- **F5** - Quick build and view
- **Ctrl+Shift+C** - Clean build (removes temp files)
- **Ctrl+Shift+B** - Full build with bibliography

### Create Submission Package:
- **Tools → User → Create:Submission**
- Or run: `build.bat submission`

## 📦 Build Scripts Usage

### Windows Command Line:
```batch
# Full build (default)
build.bat

# Quick build
build.bat quick

# Clean temp files
build.bat clean

# Create submission package
build.bat submission
```

### Features:
- Automatic XeLaTeX compilation
- Bibliography processing with Biber
- Creates dated submission files
- Copies all figures to submission folder

## 🔍 Verification Checklist

### 1. Check XeLaTeX Installation:
Open Command Prompt and run:
```
xelatex --version
```
Should show XeTeX version info.

### 2. Test Build:
```
cd LaTeX
build.bat quick
```
Should create `main.pdf` without errors.

### 3. Check fontspec:
Your document should compile because fontspec is properly configured for XeLaTeX.

## 🐛 Troubleshooting

### "Command not found: xelatex"
- Install/update MiKTeX or TeX Live
- Ensure LaTeX is in system PATH

### "Package fontspec Error"
- Confirm you're using XeLaTeX (not pdfLaTeX)
- Check TeXstudio build configuration

### Bibliography not updating:
1. Clean build: `build.bat clean`
2. Full build: `build.bat full`

### PDF locked/not updating:
- Close external PDF viewers
- Use TeXstudio's internal viewer

## 📋 Project Files Created/Updated:

✅ **Updated for XeLaTeX:**
- `tools/build.bat` - Windows build script
- `tools/build.sh` - Unix build script  
- `tools/Makefile` - Make build script
- `TEXSTUDIO_WINDOWS_SETUP.md` - Configuration guide

✅ **New Files:**
- `build.bat` - Main build entry point
- `.gitignore` - Git ignore patterns
- `Paper2_Materials.txss` - TeXstudio session file

✅ **Directory Structure:**
- `submission/` - For final submission files
- `tools/` - Build scripts and utilities

Your project is now properly configured for XeLaTeX with TeXstudio on Windows 11!