install: install-flit
	flit install --deps develop

develop: install-flit
	flit install --deps all --pth-file

install-flit:
	python -m pip install --upgrade pip
	pip install flit

isort-src:
	isort ./imxInsightsCli ./tests

isort-docs:
	isort ./docs -o imxInsightsCli

isort-examples:
	isort ./examples -o imxInsightsCli -p app

format: isort-src isort-docs isort-examples
	black .

isort-src-check:
	isort --check-only ./imxInsightsCli ./tests

isort-docs-check:
	isort --check-only ./docs -o imxInsightsCli

isort-examples-check:
	isort --check-only ./examples -o imxInsightsCli -p app

format-check: isort-src-check isort-docs-check
	black --check .

lint:
	flake8 ./imxInsightsCli ./tests

typecheck:
	mypy imxInsightsCli/ tests/

# todo: make sure in production covar is at least 90%
test:
	pytest --cov=imxInsightsCli/ --cov-report=term-missing --cov-fail-under=80

bumpversion-major:
	bumpversion major

bumpversion-minor:
	bumpversion minor

bumpversion-patch:
	bumpversion patch

bumpversion-build:
	bumpversion build
	
build-wheel:
	flit build

docs-serve:
	mkdocs serve

docs-publish:
	mkdocs build
# 	mkdocs gh-deploy

check-all: test lint typecheck # docs-publish

check: lint typecheck

build-cli-app:
	python -m PyInstaller imxInsightsCli/imx_diff/imx_to_excel.py --onefile --add-data ".venv/Lib/site-packages/imxInsights/custom_puic_config.yaml:imxInsights/."
