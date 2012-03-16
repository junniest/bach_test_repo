
DOC := paper
PKG := $(DOC)-$(shell date +%F).tar.gz
all: paper.pdf

paper.pdf: paper.tex intro.tex parser-model.tex dynamic-extensions.tex
	pdflatex $(DOC).tex
	bibtex $(DOC)
	pdflatex $(DOC).tex
	pdflatex $(DOC).tex

clean:
	$(RM) *.aux *.dvi *.pdf *.log *.tex.bak *.blg *.bbl

dist:
	mkdir -p .dist/paper-dist/
	cp -r Makefile *.tex $(DOC).bib .dist/paper-dist/
	( cd .dist && tar zvcf $(PKG) paper-dist/ )
	mv .dist/$(PKG) .
	rm -rf .dist/

