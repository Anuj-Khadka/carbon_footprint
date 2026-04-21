# latexmk configuration for paper/
# Run:  latexmk -pvc      (watch & rebuild)
# Run:  latexmk           (one-shot build)
# Run:  latexmk -c        (clean aux files, keep PDF)
# Run:  latexmk -C        (clean everything including PDF)

$pdf_mode  = 1;  # build PDF via pdflatex
$bibtex_use = 2; # always run biber when the .bcf says so

$pdflatex = 'pdflatex -interaction=nonstopmode -halt-on-error -synctex=1 %O %S';

# Force biber (biblatex backend) instead of bibtex
$biber = 'biber %O %S';

# Files to also clean with `latexmk -c`
$clean_ext = 'bbl run.xml synctex.gz';
