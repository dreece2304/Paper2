@echo off
REM Build script for LaTeX manuscript on Windows
REM Usage: build.bat [clean|full|quick|submission]

cd /d "%~dp0\.."

if "%1"=="" goto full
if "%1"=="clean" goto clean
if "%1"=="full" goto full  
if "%1"=="quick" goto quick
if "%1"=="submission" goto submission
goto help

:clean
echo Cleaning auxiliary files...
cd High_Throughput_MLD_for_Advanced_EUV_Photoresists__Stability_and_Performance_of_Organic_Inorganic_Hybrid_Films__Copy_
del /q *.aux *.bbl *.bcf *.blg *.log *.out *.run.xml *.toc *.lof *.lot *.synctex.gz 2>nul
del /q sections\*.aux 2>nul
echo Clean complete!
goto end

:quick
echo Quick build (single pass)...
cd High_Throughput_MLD_for_Advanced_EUV_Photoresists__Stability_and_Performance_of_Organic_Inorganic_Hybrid_Films__Copy_
xelatex -interaction=nonstopmode main.tex
echo Quick build complete!
goto end

:full
echo Full build with bibliography...
cd High_Throughput_MLD_for_Advanced_EUV_Photoresists__Stability_and_Performance_of_Organic_Inorganic_Hybrid_Films__Copy_

echo Pass 1/4: Initial compilation...
xelatex -interaction=nonstopmode main.tex

echo Pass 2/4: Bibliography processing...
biber main

echo Pass 3/4: Incorporating bibliography...
xelatex -interaction=nonstopmode main.tex

echo Pass 4/4: Final compilation...
xelatex -interaction=nonstopmode main.tex

echo Full build complete!
echo Output: main.pdf
goto end

:submission
echo Preparing submission files...
cd High_Throughput_MLD_for_Advanced_EUV_Photoresists__Stability_and_Performance_of_Organic_Inorganic_Hybrid_Films__Copy_

REM Full build first
call :full

REM Create submission directory
if not exist "submission" mkdir submission
if not exist "submission\figures" mkdir submission\figures

REM Copy PDF with date stamp
for /f "tokens=2 delims==" %%I in ('wmic os get localdatetime /value') do set datetime=%%I
set datetime=%datetime:~0,8%
copy main.pdf "submission\manuscript_%datetime%.pdf"

REM Copy figures
copy Figures\*.tiff submission\figures\
copy Figures\*.pdf submission\figures\

REM Create file list
echo Submission files created: > submission\README.txt
echo - manuscript_%datetime%.pdf >> submission\README.txt
echo - figures\ (all figure files) >> submission\README.txt
echo. >> submission\README.txt
echo Journal: Journal of Materials Chemistry A >> submission\README.txt
echo Date: %date% %time% >> submission\README.txt

echo Submission package created in submission\
goto end

:help
echo Usage: build.bat [command]
echo Commands:
echo   clean      - Remove auxiliary files
echo   quick      - Single compilation pass
echo   full       - Full build with bibliography (default)
echo   submission - Create submission package
goto end

:end
pause