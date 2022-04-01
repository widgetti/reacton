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

components: react_ipywidgets/ipywidgets.py react_ipywidgets/bqplot.py react_ipywidgets/ipyvue.py react_ipywidgets/ipyvuetify.py

react_ipywidgets/ipywidgets.py: react_ipywidgets/generate.py
	python -m react_ipywidgets.ipywidgets

react_ipywidgets/bqplot.py: react_ipywidgets/generate.py
	python -m react_ipywidgets.bqplot
	python -c "import react_ipywidgets.bqplot"

react_ipywidgets/ipyvue.py: react_ipywidgets/generate.py
	python -m react_ipywidgets.ipyvue

react_ipywidgets/ipyvuetify.py: react_ipywidgets/generate.py
	python -m react_ipywidgets.ipyvuetify


# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
# %: Makefile
# 	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
