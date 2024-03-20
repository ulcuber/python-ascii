venv:
	python -m venv .

# . ./bin/activate before make
install:
	pip install -r ./requirements.txt
clean:
	pip uninstall -r ./requirements.txt
test:
	python -m unittest discover -f -s tests -t .
lint:
	python -m ruff ./src
lint-fix:
	python -m ruff --fix ./src
