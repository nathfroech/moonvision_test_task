.PHONY: requirements
requirements:
	@bash helpers/update_requirements.sh

.PHONY: lint
lint:
	@pre-commit run --all-files

.PHONY: test
test:
	@PROJECT_ENVIRONMENT=test pytest -c setup.cfg

.PHONY: coverage
coverage:
	@PROJECT_ENVIRONMENT=test pytest -c setup.cfg --cov-config setup.cfg -s --cov-report term --cov .

.PHONY: env_file
env_file:
	@python helpers/generate_env_file.py

.PHONY: init_project
init_project: requirements env_file
	pre-commit autoupdate
	pre-commit install

.PHONY: clean_pyc
clean_pyc: ## remove Python file artifacts
	find . -name '*.pyc' -delete
	find . -name '*.pyo' -delete
	## Files with tilde at the end of their name are backup files, created by some editors
	find . -name '*~' -delete
	find . -name '__pycache__' -delete

.PHONY: clean_test
clean_test: ## remove test and coverage artifacts
	rm -rf .tox/
	rm -f .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/

.PHONY: clean
clean: clean_pyc clean_test ## remove all test, coverage and Python artifacts

.PHONY: clean_ignored
clean_ignored: ## remove all files, listed in .gitignore
	git clean -fxd

.PHONY: clean_ignored_with_git
clean_ignored_with_git: clean_ignored ## remove all files, listed in .gitignore, and .git directory itself
	rm -rf .git/
