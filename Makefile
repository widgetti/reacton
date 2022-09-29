# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?=
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = source
BUILDDIR      = build

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

.PHONY: help Makefile components

components: reacton/ipywidgets.py reacton/bqplot.py reacton/ipyvue.py reacton/ipyvuetify.py reacton/ipycanvas.py

reacton/ipywidgets.py: reacton/generate.py
	python -m reacton.ipywidgets

reacton/bqplot.py: reacton/generate.py
	python -m reacton.bqplot
	python -c "import reacton.bqplot"

reacton/ipyvue.py: reacton/generate.py
	python -m reacton.ipyvue

reacton/ipyvuetify.py: reacton/generate.py
	python -m reacton.ipyvuetify

reacton/ipycanvas.py: reacton/generate.py
	python -m reacton.ipycanvas

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
# %: Makefile
# 	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
