.PHONY: lint

lint:
	pip install --upgrade pip
	pip install flake8
	flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics
