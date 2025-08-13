% mymanuscript.cls
\NeedsTeXFormat{LaTeX2e}
\ProvidesClass{mymanuscript}[2024/11/19 Custom Class for Scientific Manuscript]
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

% --- Detect Supplementary Mode ---
\newif\ifSI
\SIfalse
\DeclareOption{supplementary}{\SItrue}
\DeclareOption*{\PassOptionsToClass{\CurrentOption}{article}}
\ProcessOptions\relax

\LoadClass[12pt]{article}

% Essential Packages
\RequirePackage{geometry}
\geometry{a4paper, margin=1in}
\RequirePackage{graphicx}

% Configure graphics for XeLaTeX with TIFF support
\DeclareGraphicsExtensions{.pdf,.png,.jpg,.jpeg,.tiff,.tif}
\DeclareGraphicsRule{.tiff}{png}{.png}{`convert #1 \noexpand\OutputFile}
\DeclareGraphicsRule{.tif}{png}{.png}{`convert #1 \noexpand\OutputFile}
\RequirePackage{xcolor}
\RequirePackage{amsmath, amsfonts, amssymb}
\RequirePackage{titlesec}
\RequirePackage{fancyhdr}
\RequirePackage{float}
\RequirePackage{setspace}
\RequirePackage{array}     % For custom column types and table adjustments
\RequirePackage{booktabs}  % For professional-quality table lines
\RequirePackage{caption}   % For caption formatting
\RequirePackage{multirow}  % For multirow table cells
\RequirePackage{chemfig}   % For chemical structures
\RequirePackage[version=4]{mhchem}    % For chemical equations and formulas
\RequirePackage{siunitx}   % For SI units and measurements
\RequirePackage{hyperref}  % Load hyperref last

% Configure siunitx
\sisetup{
    per-mode=symbol,
    separate-uncertainty=true,
    inter-unit-product=\ensuremath{{}\cdot{}},
    group-separator={,}
}

% Define Custom Units for siunitx
\DeclareSIUnit\Molar{M}     % Define \Molar to print as "M"
\DeclareSIUnit\molar{M}     % Define \molar to print as "M" 
\DeclareSIUnit\angstrom{\text{Å}}  % Define angstrom unit
\DeclareSIUnit\cycle{cycle}         % Define cycle unit
\RequirePackage[
    backend=biber,
    style=nature,
    maxbibnames=6,
    sorting=none,
    natbib=true            % Enables \cite{...} command
]{biblatex}
\addbibresource{bibliography/references_updated.bib}

% Additional custom units
\DeclareSIUnit{\torr}{Torr} % Define Torr as a unit
\DeclareSIUnit{\mTorr}{mTorr} % Define mTorr explicitly (optional)

% Line Spacing
\setstretch{1.5}

% Section Formatting (Unnumbered)
\titleformat{\section}[block]
  {\Large\bfseries\sffamily} % Large, bold, sans-serif font
  {}                         % No numbering
  {0em}                      % No spacing for a number
  {}

\titlespacing*{\section}{0pt}{2em}{1em}

\titleformat{\subsection}[block]
  {\normalsize\itshape\sffamily} % Italic, sans-serif font for subsections
  {}                              % No numbering
  {0em}                           % No spacing for a number
  {}

\titlespacing*{\subsection}{0pt}{1.5em}{0.5em}

% Header and Footer
\pagestyle{fancy}
\fancyhf{}
\setlength{\headheight}{15pt}  % Fix header height warning
\fancyhead[C]{\textit{\nouppercase{\leftmark}}}
\fancyfoot[C]{\thepage}

% Commands for Author and Affiliations
\newcommand{\authorinfo}[2]{#1$^{#2}$}
\newcommand{\affiliation}[2]{$^{#1}$#2 \\}

% Bibliography
\addbibresource{bibliography/references_updated.bib}

% Hyperlink Setup
\hypersetup{
  colorlinks=true,
  linkcolor=blue,
  citecolor=black,
  urlcolor=blue,
  pdftitle={\@title},
  pdfauthor={\@author},
  pdfkeywords={}
}

% --- Table Adjustments ---

% Increase Row Height
\renewcommand{\arraystretch}{1.5} % Adjusts the vertical space between rows (default is 1)

% Adjust Column Separation
\setlength{\tabcolsep}{6pt} % Adjusts horizontal space between columns (default is 6pt)

% Define Custom Column Types
\newcolumntype{P}[1]{>{\hspace{0.5em}\arraybackslash}p{#1}<{\hspace{0.5em}}} % Paragraph column with padding
\newcolumntype{M}[1]{>{\centering\arraybackslash}m{#1}}                      % Centered column with vertical centering

% Booktabs Parameters (Adjust as needed)
\setlength{\heavyrulewidth}{0.2em} % Thickness of \toprule and \bottomrule (default 0.08em)
\setlength{\lightrulewidth}{0.05em} % Thickness of \midrule (default 0.05em)
\setlength{\cmidrulewidth}{0.03em}  % Thickness of \cmidrule (default 0.03em)
\setlength{\belowrulesep}{0.65ex}   % Space below \toprule or \midrule
\setlength{\aboverulesep}{0.4ex}    % Space above \midrule or \bottomrule
\setlength{\cmidrulesep}{\doublerulesep} % Space between adjacent \cmidrule lines
\setlength{\cmidrulekern}{0.5em}    % Space on either side of \cmidrule

% --- Global chemfig Settings ---

% Set global parameters for chemfig diagrams using point units
\setchemfig{
  atom sep=25pt,                   % Bond length between atoms (standard ~25pt)
  bond style={line width=0.6pt},   % Standard bond line width
  bond offset=1pt,                 % Spacing between multiple bonds (double, triple)
  cram width=3pt,                  % Width of wedge bonds
  cram dash pattern=on 1pt off 1pt,% Pattern for dashed wedge bonds
  angle increment=30,              % Default angle for unspecified bonds
  double bond sep=2pt,             % Separation between lines in double bonds
  fixed length=true,               % Use fixed bond lengths
  atom style={scale=0.9},          % Scale for atomic labels
  atom style/.style={
    \fontsize{9pt}{9pt}\selectfont,% Font size for atomic labels
    \chemfig@atom@style
  }
}
% --- Supplementary Numbering Overrides ---
\ifSI
  \renewcommand{\thefigure}{S\arabic{figure}}
  \renewcommand{\thetable}{S\arabic{table}}
  \renewcommand{\theequation}{S\arabic{equation}}
  \renewcommand{\figurename}{Supplementary Figure}
  \renewcommand{\tablename}{Supplementary Table}
\fi

\endinput
