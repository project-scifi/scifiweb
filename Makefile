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
dev: venv scifiweb/static/scss/site.scss.css
	venv/bin/python manage.py runserver 0.0.0.0:8000

.PHONY: clean
clean:
	rm -rf venv .tox
	venv/bin/coverage erase

.PHONY: scss
scss: scifiweb/static/scss/site.scss.css

# phony because it depends on other files, too many to express
.PHONY: scifiweb/static/scss/site.scss.css
scifiweb/static/scss/site.scss.css: scifiweb/static/scss/site.scss venv
	@# In prod, compile with --style compressed
	venv/bin/sassc --sourcemap "$<" "$@"
