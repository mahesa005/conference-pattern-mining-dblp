#!/bin/sh
# Kompilasi penuh: xelatex, biber, xelatex x2
cd "$(dirname "$0")"
xelatex -interaction=nonstopmode -file-line-error Laporan.tex >/dev/null 2>&1
biber Laporan >/dev/null 2>&1
xelatex -interaction=nonstopmode -file-line-error Laporan.tex >/dev/null 2>&1
xelatex -interaction=nonstopmode -file-line-error Laporan.tex 2>&1 | grep -E "^! |^\./.*:[0-9]+:|Output written|undefined|Citation|Reference .* undefined" 
