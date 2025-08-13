# LaTeX Project for Journal of Materials Chemistry A

## 🚀 Quick Start

1. **Open TeXstudio**
2. **File → Load Session** → Select `Paper2_Materials.txss`
3. **Follow setup guide:** `COMPLETE_SETUP_GUIDE.md`
4. **Press F5** to build and view

## 📚 Important Files

- **`COMPLETE_SETUP_GUIDE.md`** - Complete TeXstudio setup for Windows 11
- **`TEXSTUDIO_WINDOWS_SETUP.md`** - Detailed TeXstudio configuration
- **`build.bat`** - Main build script (run from LaTeX directory)
- **`Paper2_Materials.txss`** - TeXstudio session file

## ⚠️ Critical Information

**Your project requires XeLaTeX** (not pdfLaTeX) because you use `\usepackage{fontspec}`.

All build scripts have been configured for XeLaTeX.

## 🏗️ Build Commands

```batch
# Full build with bibliography
build.bat

# Quick single-pass build  
build.bat quick

# Clean temporary files
build.bat clean

# Create submission package
build.bat submission
```

## 📁 Directory Structure

```
LaTeX/
├── build.bat                    # Main build script
├── submission/                  # Generated submission files
├── tools/                       # Build utilities
└── High_Throughput_MLD.../     # Main manuscript
    ├── main.tex                # Main document
    ├── sections/               # Content sections
    ├── Figures/                # TIFF figures for LaTeX
    └── bibliography/           # References
```

## 🎯 Workflow

1. **Edit** your .tex files in TeXstudio
2. **Build** with F5 or build.bat
3. **Review** PDF output
4. **Submit** using build.bat submission

## 🔧 Troubleshooting

See `COMPLETE_SETUP_GUIDE.md` for detailed troubleshooting instructions.

**Most common issues:**
- Using pdfLaTeX instead of XeLaTeX
- Missing MiKTeX/TeX Live packages
- PDF viewer conflicts