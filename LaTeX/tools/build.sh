#!/bin/bash
# Build script for LaTeX manuscript on Unix/Linux/WSL
# Usage: ./build.sh [clean|full|quick|submission]

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
MANUSCRIPT_DIR="${SCRIPT_DIR}/High_Throughput_MLD_for_Advanced_EUV_Photoresists__Stability_and_Performance_of_Organic_Inorganic_Hybrid_Films__Copy_"

# Change to manuscript directory
cd "$MANUSCRIPT_DIR" || exit 1

# Function definitions
clean() {
    echo -e "${YELLOW}Cleaning auxiliary files...${NC}"
    rm -f *.aux *.bbl *.bcf *.blg *.log *.out *.run.xml *.toc *.lof *.lot *.synctex.gz
    rm -f sections/*.aux
    echo -e "${GREEN}Clean complete!${NC}"
}

quick_build() {
    echo -e "${YELLOW}Quick build (single pass)...${NC}"
    xelatex -interaction=nonstopmode main.tex
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}Quick build complete!${NC}"
    else
        echo -e "${RED}Build failed!${NC}"
        exit 1
    fi
}

full_build() {
    echo -e "${YELLOW}Full build with bibliography...${NC}"
    
    echo -e "${YELLOW}Pass 1/4: Initial compilation...${NC}"
    xelatex -interaction=nonstopmode main.tex || { echo -e "${RED}Pass 1 failed!${NC}"; exit 1; }
    
    echo -e "${YELLOW}Pass 2/4: Bibliography processing...${NC}"
    biber main || { echo -e "${RED}Biber failed!${NC}"; exit 1; }
    
    echo -e "${YELLOW}Pass 3/4: Incorporating bibliography...${NC}"
    xelatex -interaction=nonstopmode main.tex || { echo -e "${RED}Pass 3 failed!${NC}"; exit 1; }
    
    echo -e "${YELLOW}Pass 4/4: Final compilation...${NC}"
    xelatex -interaction=nonstopmode main.tex || { echo -e "${RED}Pass 4 failed!${NC}"; exit 1; }
    
    echo -e "${GREEN}Full build complete!${NC}"
    echo -e "${GREEN}Output: main.pdf${NC}"
}

submission() {
    echo -e "${YELLOW}Preparing submission files...${NC}"
    
    # Full build first
    full_build
    
    # Create submission directory structure
    mkdir -p submission/figures
    
    # Copy PDF with date stamp
    DATE=$(date +%Y%m%d)
    cp main.pdf "submission/manuscript_${DATE}.pdf"
    
    # Copy figures
    cp Figures/*.tiff submission/figures/ 2>/dev/null
    cp Figures/*.pdf submission/figures/ 2>/dev/null
    
    # Create README
    cat > submission/README.txt << EOF
Submission files created: $(date)
- manuscript_${DATE}.pdf
- figures/ (all figure files)

Journal: Journal of Materials Chemistry A
Date: $(date)

Checklist:
[ ] All figures referenced in text
[ ] Line spacing set to 2.0
[ ] Author information complete
[ ] Conflicts of interest stated
[ ] Data availability statement included
EOF
    
    echo -e "${GREEN}Submission package created in submission/${NC}"
}

watch_mode() {
    echo -e "${YELLOW}Watch mode: Auto-rebuild on file changes${NC}"
    echo "Press Ctrl+C to stop"
    
    while true; do
        inotifywait -q -e modify,create,delete -r . --exclude '\.git|\.aux|\.log|\.pdf' && {
            echo -e "${YELLOW}Changes detected, rebuilding...${NC}"
            quick_build
        }
    done
}

# Main script logic
case "$1" in
    clean)
        clean
        ;;
    quick)
        quick_build
        ;;
    full|"")
        full_build
        ;;
    submission)
        submission
        ;;
    watch)
        watch_mode
        ;;
    *)
        echo "Usage: $0 [clean|quick|full|submission|watch]"
        echo "Commands:"
        echo "  clean      - Remove auxiliary files"
        echo "  quick      - Single compilation pass"
        echo "  full       - Full build with bibliography (default)"
        echo "  submission - Create submission package"
        echo "  watch      - Auto-rebuild on file changes (requires inotify-tools)"
        exit 1
        ;;
esac