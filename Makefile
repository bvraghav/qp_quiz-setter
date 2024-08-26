SHELL           := /usr/bin/zsh

# -----------------------------------------------------
# CONFIG
# -----------------------------------------------------
NUM_SETS	:= 1


# -----------------------------------------------------
# CODE STARTS
# -----------------------------------------------------
# Variables

conda-activate	:= source ~/miniconda3/bin/activate emacs
python		:= $(conda-activate); python

SEEDS		:= $(shell $(python) -m seeds -n $(NUM_SETS))

ORG_FILES	:= $(SEEDS:%=dist/qp-%.org)
TEX_FILES	:= $(SEEDS:%=dist/qp-%.tex)
PDF_FILES	:= $(SEEDS:%=dist/qp-%.pdf)

# Create all sets separately and key file separately
all : dist/all-sets.pdf dist/key.pdf

# Clean the working copy
clean :
	rm -rf dist

# Clean the dist of `_minted*' directories
clean-minted :
	rm -rf dist/_minted*

# Create single pdf for all sets
dist/all-sets.pdf : ${PDF_FILES}
	pdftk $^ cat output $@

# Create pdf from tex
dist/%.pdf: dist/%.tex
	cd dist; latexmk $*.tex; latexmk -c $*.tex

# Create tex from org
%.tex: %.org
	fire_emacs -nf -- -e '(with-current-buffer (find-file-noselect "$(shell pwd)/$<") (org-latex-export-to-latex) (kill-buffer))'

# Create org using python setter.py
dist/qp-%.org : dist dist/images
	$(python) -m setter -s $* > $@

# Create key from org files
dist/key.org : ${ORG_FILES}
	{ \
	  echo '#+options: toc:nil' ; \
	  for FNAME in $^ ; do  \
	  SET=$${FNAME##dist/qp-} ; SET=$${SET%%.org} ; \
	  echo -n "+ Set $${SET:u} :: "; \
	  cat $${FNAME} | tail -1 | tr -d '#' ; done \
	} > $@

# Create dist folder
dist :
	mkdir -p dist

# Copy images from current folder to dist.  Necessary
# for `tiet-question-paper' latex class.
dist/images : images dist
	cp -r images dist/

ifeq ($(IMAGES_URL),)
# Fallback for graceful degradation.
images :
	mkdir -p images
else
# If public, insert images folder by downloading and
# decompressing.
images : images.zip
	wget $(IMAGES_URL)
	unzip images.zip
endif
