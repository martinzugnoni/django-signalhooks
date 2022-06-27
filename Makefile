.PHONY: test build

TAG="\n\n\033[0;32m\#\#\# "
END=" \#\#\# \033[0m\n"

PYTHONPATH=.
DJANGO_SETTINGS=tests.settings

django-command = poetry run django-admin $(1) $(2) --settings $(DJANGO_SETTINGS) --pythonpath $(PYTHONPATH)


test:
	@echo $(TAG)Running Tests$(END)
	PYTHONPATH=$(PYTHONPATH) DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS) poetry run pytest --cov=signalhooks --cov-report term-missing  tests

build:
	@echo $(TAG)Building Project$(END)
	poetry run black . --check
	poetry run pylint --rcfile=.pylintrc signalhooks/*
	PYTHONPATH=$(PYTHONPATH) DJANGO_SETTINGS_MODULE=$(DJANGO_SETTINGS) poetry run pytest --cov=signalhooks --cov-config=.coveragerc   --cov-fail-under=90 tests
