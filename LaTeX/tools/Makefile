# Makefile for LaTeX manuscript compilation
# Usage: make [target]

# Variables
MANUSCRIPT_DIR = High_Throughput_MLD_for_Advanced_EUV_Photoresists__Stability_and_Performance_of_Organic_Inorganic_Hybrid_Films__Copy_
MAIN = main
LATEX = xelatex
BIBTEX = biber
LATEX_FLAGS = -interaction=nonstopmode
DATE := $(shell date +%Y%m%d)

# Directories
BUILD_DIR = build
SUBMISSION_DIR = submission

# File patterns
AUX_FILES = *.aux *.bbl *.bcf *.blg *.log *.out *.run.xml *.toc *.lof *.lot *.synctex.gz
TEX_FILES = $(MANUSCRIPT_DIR)/*.tex $(MANUSCRIPT_DIR)/sections/*.tex
BIB_FILES = $(MANUSCRIPT_DIR)/bibliography/*.bib

# Phony targets
.PHONY: all clean full quick submission help watch

# Default target
all: full

# Full build with bibliography
full:
	@echo "Full build with bibliography..."
	@cd $(MANUSCRIPT_DIR) && \
		$(LATEX) $(LATEX_FLAGS) $(MAIN).tex && \
		$(BIBTEX) $(MAIN) && \
		$(LATEX) $(LATEX_FLAGS) $(MAIN).tex && \
		$(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	@echo "Build complete! Output: $(MANUSCRIPT_DIR)/$(MAIN).pdf"

# Quick build (single pass)
quick:
	@echo "Quick build (single pass)..."
	@cd $(MANUSCRIPT_DIR) && $(LATEX) $(LATEX_FLAGS) $(MAIN).tex
	@echo "Quick build complete!"

# Clean auxiliary files
clean:
	@echo "Cleaning auxiliary files..."
	@cd $(MANUSCRIPT_DIR) && rm -f $(AUX_FILES)
	@cd $(MANUSCRIPT_DIR)/sections && rm -f *.aux
	@echo "Clean complete!"

# Deep clean (including PDF)
distclean: clean
	@echo "Removing PDF files..."
	@cd $(MANUSCRIPT_DIR) && rm -f *.pdf
	@echo "Deep clean complete!"

# Create submission package
submission: full
	@echo "Creating submission package..."
	@mkdir -p $(MANUSCRIPT_DIR)/$(SUBMISSION_DIR)/figures
	@cd $(MANUSCRIPT_DIR) && \
		cp $(MAIN).pdf $(SUBMISSION_DIR)/manuscript_$(DATE).pdf && \
		cp Figures/*.tiff $(SUBMISSION_DIR)/figures/ 2>/dev/null || true && \
		cp Figures/*.pdf $(SUBMISSION_DIR)/figures/ 2>/dev/null || true
	@echo "Submission package created in $(MANUSCRIPT_DIR)/$(SUBMISSION_DIR)/"
	@echo "Manuscript: manuscript_$(DATE).pdf"

# Watch for changes and auto-rebuild
watch:
	@echo "Watching for changes... (requires inotify-tools)"
	@while true; do \
		inotifywait -q -e modify,create,delete -r $(MANUSCRIPT_DIR) \
			--exclude '\.git|\.aux|\.log|\.pdf|\.bbl' && \
		make quick; \
	done

# Count words (approximate)
wordcount:
	@echo "Approximate word count:"
	@cd $(MANUSCRIPT_DIR) && \
		texcount -inc -total main.tex | grep "Words in text"

# Check for common LaTeX issues
check:
	@echo "Checking for common issues..."
	@cd $(MANUSCRIPT_DIR) && \
		echo "Undefined references:" && \
		grep -n "Warning: Reference" *.log 2>/dev/null || echo "  None found" && \
		echo "Undefined citations:" && \
		grep -n "Warning: Citation" *.log 2>/dev/null || echo "  None found" && \
		echo "Overfull boxes:" && \
		grep -n "Overfull" *.log 2>/dev/null | head -5 || echo "  None found"

# Help target
help:
	@echo "LaTeX Makefile targets:"
	@echo "  make              - Full build with bibliography (default)"
	@echo "  make quick        - Single compilation pass"
	@echo "  make clean        - Remove auxiliary files"
	@echo "  make distclean    - Remove all generated files including PDF"
	@echo "  make submission   - Create submission package"
	@echo "  make watch        - Auto-rebuild on file changes"
	@echo "  make wordcount    - Approximate word count"
	@echo "  make check        - Check for common LaTeX issues"
	@echo "  make help         - Show this help message"