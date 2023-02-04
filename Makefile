init:
	pip install -r requirements.txt
	mkdir -p ./logs

install_dev_package:
	pip install -r requirements_dev.txt

make_log:
	python scripts/make_log_file.py --filename=/tmp/random.log --filesize=1073741824

run:
	python main.py

unit:
	python -m pytest tests/unit

black:
	black .

isort:
	isort .

clean:
	find . | grep -E "(/__pycache__$|\.pyc$|\.pyo$)" | xargs rm -rf
	rm logs/*.log
	rm -rf .pytest_cache

pretty: isort black

