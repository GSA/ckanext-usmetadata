.PHONY: lint

lint:
	pip install --upgrade pip
	pip install flake8
	flake8 . --count --ignore E501 --show-source --statistics
