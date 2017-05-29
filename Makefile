.PHONY: test
test: export SCIFIWEB_TESTING ?= 1
test: venv
	venv/bin/tox

.PHONY: coveralls
coveralls: venv test
	venv/bin/coveralls

.PHONY: install-hooks
install-hooks: venv
	venv/bin/pre-commit install

venv: requirements.txt requirements-dev.txt
	vendor/venv-update \
		venv= -ppython3 venv \
		install= -r requirements.txt -r requirements-dev.txt

.PHONY: update-requirements
update-requirements: venv
	venv/bin/upgrade-requirements

.PHONY: dev
dev: export SCIFIWEB_DEBUG ?= 1
dev: venv
	venv/bin/python manage.py runserver 0.0.0.0:8000

.PHONY: clean
clean:
	rm -rf venv .tox
	venv/bin/coverage erase
