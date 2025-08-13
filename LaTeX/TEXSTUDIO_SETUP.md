# TeXstudio Setup Guide for Your Paper

## 1. Initial Setup

### Install TeXstudio (if not already installed)
- Windows: Download from https://www.texstudio.org/
- Install with default settings

### Open Your Project
1. Launch TeXstudio
2. File → Open → Navigate to your main.tex
3. File → Save All

## 2. Configure Build Commands

### Go to Options → Configure TeXstudio → Build

Set the following:

**Default Compiler:** PdfLaTeX
**Default Bibliography Tool:** Biber
**Default Viewer:** Internal PDF Viewer

**Build & View:** 
```
txs:///compile | txs:///bibliography | txs:///compile | txs:///compile | txs:///view-pdf-internal
```

### Custom User Commands (Options → Configure TeXstudio → Build → User Commands)

Add these useful commands:

1. **Clean Auxiliary Files:**
   ```
   cmd /c del *.aux *.bbl *.bcf *.blg *.log *.out *.run.xml *.toc *.lof *.lot
   ```

2. **Full Clean:**
   ```
   cmd /c del *.aux *.bbl *.bcf *.blg *.log *.out *.run.xml *.toc *.lof *.lot *.pdf
   ```

3. **Create Submission Version:**
   ```
   cmd /c copy main.pdf submission\manuscript_%date:~-4%%date:~-10,2%%date:~-7,2%.pdf
   ```

## 3. Editor Configuration

### Go to Options → Configure TeXstudio → Editor

- **Font Family:** Consolas or Courier New
- **Font Size:** 11pt
- **Tab Width:** 4
- **Insert Spaces for Tab:** Yes
- **Show Line Numbers:** Yes
- **Show Whitespace:** Yes (helpful for tables)
- **Word Wrap:** Soft wrap at window edge

### Syntax Highlighting
- Enable all LaTeX highlighting
- Custom highlighting for your commands

## 4. Project-Specific Settings

### Create a TeXstudio Project Session

1. **File → Save Session**
   - Save as: `Paper2_TeXstudio.txss`
   - This saves all open files and cursor positions

2. **Define Master Document**
   - Right-click on `main.tex` → Set as Master Document
   - This ensures correct compilation from any section file

### Set up Quick Build
- Tools → Commands → Quick Build
- Configure as: PdfLaTeX + Bib(la)tex + PdfLaTeX (x2) + View

## 5. Useful Shortcuts

### Essential TeXstudio Shortcuts:
- **F1**: Quick Build (compile)
- **F5**: Build & View
- **F7**: View PDF
- **Ctrl+Click** on PDF: Jump to source
- **Ctrl+Space**: Auto-completion
- **Ctrl+E**: Insert environment
- **Ctrl+Shift+M**: Insert math
- **Ctrl+/**: Comment/uncomment
- **Ctrl+T**: Toggle between .tex and PDF

### Navigation:
- **Ctrl+G**: Go to line
- **F2**: Go to next marker/error
- **Ctrl+Shift+F2**: Go to previous marker

## 6. Templates and Macros

### Add Custom Macros (Macros → Edit Macros)

1. **Insert Figure:**
```latex
\begin{figure}[htbp]
    \centering
    \includegraphics[width=0.8\textwidth]{figures/%|}
    \caption{%|}
    \label{fig:%|}
\end{figure}
```

2. **Insert Table:**
```latex
\begin{table}[htbp]
    \centering
    \caption{%|}
    \label{tab:%|}
    \begin{tabular}{%|}
        \toprule
        %|
        \midrule
        %|
        \bottomrule
    \end{tabular}
\end{table}
```

3. **Chemical Formula:**
```latex
\ce{%|}
```

## 7. Spell Checking

### Configure Dictionary
- Options → Configure TeXstudio → Language Checking
- Download English (US) dictionary
- Enable inline spell checking
- Add scientific terms to user dictionary

## 8. Advanced Features

### Structure View
- View → Structure
- Shows document outline
- Click to navigate

### PDF Synchronization
- Forward search: Ctrl+Click in source
- Backward search: Ctrl+Click in PDF

### Live Preview (for equations)
- Options → Configure TeXstudio → Preview
- Enable inline preview for math

## 9. Version Control Integration

If using Git:
- Tools → Commands → Edit User Commands
- Add: `git add -A && git commit -m "WIP: %a" && git push`

## 10. Troubleshooting

### Common Issues:

1. **Bibliography not updating:**
   - Delete .bbl and .bcf files
   - Run full build sequence

2. **PDF locked:**
   - Close external PDF viewers
   - Use internal viewer

3. **Missing packages:**
   - Use MiKTeX Console to install
   - Or TeX Live Manager (tlmgr)

### Error Checking:
- View → Log
- View → Messages
- Check for warnings and errors