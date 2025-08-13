# Manuscript Template

This is a modular LaTeX template for scientific publications. 

## Usage
1. Add content in `sections/`.
2. Place figures in `figures/` and tables in `tables/`.
3. Compile `main.tex` to produce the PDF.

## Features
- Modular sections for ease of writing and collaboration.
- Preconfigured styles for figures, tables, and captions.
- Built-in bibliography management.

## Compilation
Run the following:
```bash
pdflatex main.tex
biber main
pdflatex main.tex
pdflatex main.tex
