SHELL   := /bin/bash
VERSION := $(shell cat VERSION)
NULL    := /dev/null
STAMP   := $(shell date +%Y%m%d-%H%M)
ZIP_FILE:= $(shell basename $(PWD))-$(STAMP).zip

REQUIRE_TXT	:= requirements.txt


all: test


freeze:
	$(VIRTUAL_ENV)/bin/pip freeze > $(REQUIRE_TXT)

setup:
	$(VIRTUAL_ENV)/bin/pip install -r $(REQUIRE_TXT)

test:
	python setup.py test
	# python -m unittest discover -p "test*.py"

clean:
	@rm -rf build pysp.egg-info .eggs *.sqlite
	@(find . -name *.pyc -exec rm -rf {} \; 2>$(NULL) || true)
	@(find . -name __pycache__ -exec rm -rf {} \; 2>$(NULL) || true)

zip: clean
	@(7z a ../$(ZIP_FILE) ../$(shell basename $(PWD)))

build: test clean
	@rm -rf dist/*.whl dist/*.tar.gz
	@echo "__version__='$(VERSION)'" > pysp/__init__.py
	python setup.py sdist bdist_wheel
	@(rm pysp/__init__.py; touch pysp/__init__.py)

upload: build
	python -m twine upload \
	    dist/pysp-$(VERSION).tar.gz \
	    dist/pysp-$(VERSION)-py3-none-any.whl

install: build
	@(cd dist; ./pr pysp-$(VERSION)-py3-none-any.whl)


.PHONY: test freeze setup clean zip build upload install
