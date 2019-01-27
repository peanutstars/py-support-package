SHELL   := /bin/bash
VERSION := $(shell cat VERSION)
NULL    := /dev/null



all: test


test:
	python setup.py test
	# python -m unittest discover -p "test*.py"

clean:
	@rm -rf build pysp.egg-info .eggs *.sqlite
	@(find . -name *.pyc -exec rm -rf {} \; 2>$(NULL) || true)
	@(find . -name __pycache__ -exec rm -rf {} \; 2>$(NULL) || true)

build: test clean
	@rm -rf dist
	python setup.py sdist bdist_wheel


upload:
	python -m twine upload \
	    dist/pysp-$(VERSION).tar.gz \
	    dist/pysp-$(VERSION)-py3-none-any.whl

freeze:
	pip freeze > requirement.txt


.PHONY: test clean cleanall build upload freeze
