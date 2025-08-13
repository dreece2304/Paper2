# TeXstudio Windows 11 Setup Guide

## Quick Start Instructions

### 1. Open TeXstudio
1. Launch TeXstudio
2. File → Open → Navigate to: `Paper2\LaTeX\High_Throughput_MLD...\main.tex`

### 2. Configure TeXstudio (One-time setup)

#### Step A: Build Configuration
1. Go to: **Options → Configure TeXstudio**
2. Click on **Build** tab
3. Set these values:
   - **Default Compiler:** XeLaTeX
   - **Default Bibliography:** Biber  
   - **PDF Viewer:** Txs:///Internal PDF Viewer

#### Step B: Custom Commands
Still in Configure TeXstudio → Build:
1. Click **User Commands** (+ button to add new)
2. Add these commands:

**Clean Build:**
- Display name: `Clean:Build`
- Command: `cmd /c cd /d "%DIR%" && del *.aux *.bbl *.bcf *.blg *.log *.out *.run.xml *.synctex.gz`

**Full Build:**
- Display name: `Full:Build`  
- Command: `xelatex.exe -synctex=1 -interaction=nonstopmode %.tex | biber % | xelatex.exe -synctex=1 -interaction=nonstopmode %.tex | xelatex.exe -synctex=1 -interaction=nonstopmode %.tex`

**Submission Build:**
- Display name: `Create:Submission`
- Command: `cmd /c "%DIR%\..\build.bat" submission`

#### Step C: Editor Settings
1. Go to **Editor** tab
2. Set:
   - Font Family: **Consolas**
   - Font Size: **12**
   - Show Line Numbers: **☑ Checked**
   - Show Whitespace: **☑ Checked**
   - Tab Width: **4**

#### Step D: Shortcuts
1. Go to **Shortcuts** tab
2. Assign:
   - Build & View: **F5**
   - User:Clean:Build: **Ctrl+Shift+C**
   - User:Full:Build: **Ctrl+Shift+B**

### 3. Quick Access Toolbar
Add buttons for easy access:
1. Right-click on toolbar
2. Choose "Configure Toolbars"
3. Add:
   - Build & View
   - View PDF
   - Clean:Build
   - Full:Build

### 4. Save as Default Session
1. Open all your .tex files
2. **File → Session → Save Session**
3. Save as: `Paper2_Default.txss`
4. **File → Session → Restore Default Session** (check this option)

## Daily Workflow

### To Edit and Preview:
1. Open TeXstudio (auto-loads your session)
2. Edit your files
3. Press **F5** to build and view

### To Clean Build:
- Press **Ctrl+Shift+C** (removes temporary files)

### To Create Submission:
- Tools → User → Create:Submission

## Troubleshooting

### PDF Not Updating?
1. Close external PDF viewers
2. Use Ctrl+Shift+C to clean
3. Press F5 to rebuild

### Bibliography Issues?
- Make sure Biber is installed with your TeX distribution
- Run Full:Build command

### Missing Packages?
1. Open MiKTeX Console
2. Check for updates
3. Install missing packages