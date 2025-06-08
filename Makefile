venv:
	python -m venv .

# . ./bin/activate before make
install:
	pip install -r ./requirements.txt
clean:
	rm -rf bin etc opt include lib64 lib share pyvenv.cfg
unsinstall:
	pip uninstall -r ./requirements.txt
test:
	python -m unittest discover -f -s tests -t .
lint:
	python -m ruff check src
lint-fix:
	python -m ruff format src
