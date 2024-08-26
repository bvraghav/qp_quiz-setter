SHELL           := /usr/bin/zsh

conda-activate	:= source ~/miniconda3/bin/activate emacs
python		:= $(conda-activate); python

NUM_SETS	:= 1

SEEDS		:= $(shell $(python) -m seeds -n $(NUM_SETS))

ORG_FILES	:= $(SEEDS:%=dist/qp-%.org)
TEX_FILES	:= $(SEEDS:%=dist/qp-%.tex)
PDF_FILES	:= $(SEEDS:%=dist/qp-%.pdf)

all : ${PDF_FILES} dist/key.pdf

clean :
	rm -rf dist

clean-minted :
	rm -rf dist/_minted*

dist/%.pdf: dist/%.tex
	cd dist; latexmk $*.tex; latexmk -c $*.tex

%.tex: %.org
	fire_emacs -nf -- -e '(with-current-buffer (find-file-noselect "$(shell pwd)/$<") (org-latex-export-to-latex) (kill-buffer))'

dist/qp-%.org : dist dist/images
	$(python) -m setter -s $* > $@

dist/key.org : ${ORG_FILES}
	{ \
	  echo '#+options: toc:nil' ; \
	  for FNAME in $^ ; do  \
	  SET=$${FNAME##dist/qp-} ; SET=$${SET%%.org} ; \
	  echo -n "+ Set $${SET:u} :: "; \
	  cat $${FNAME} | tail -1 | tr -d '#' ; done \
	} > $@

dist :
	mkdir -p dist

dist/images : dist
	cp -r images dist/

