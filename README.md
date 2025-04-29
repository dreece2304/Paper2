# Paper Analysis and Figure Generation Project

## 📖 Overview
This repository supports the analysis, figure generation, and manuscript preparation for our research paper:

> "**[Insert Paper Title]**"

---

## 📂 Directory Structure

- **`01_Hybrid_Growth/`**, **`02_UV_Effects/`**, etc.:  
  Self-contained analysis subsections containing their own:
  - Raw and processed data
  - Analysis notebooks
  - Generated results (tables)
  - Figures (draft and final)

- **`shared/`**  
  Common scripts and utility functions reused across all analyses.

- **`paper/`**  
  LaTeX source for manuscript and supplementary information.

---

## ⚙️ Environment Setup
```bash
conda env create -f environment.yml
conda activate paper_analysis_env
