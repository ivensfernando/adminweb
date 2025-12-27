#include ./scripts/env.sh
TARGET_ENV_FILE=env_docker

workspace:
	python3 -m venv env
	source env/bin/activate
	python3 -m pip install -r requirements.txt

makemigrations:
	bash -c "source ./scripts/env.sh && python manage.py makemigrations"

migrate:
	bash -c "source ./scripts/env.sh && python manage.py migrate"


docker_build:
	docker build -t biidinwebapimigrations .

docker_makemigrations: docker_build
	docker run --env-file ./scripts/$(TARGET_ENV_FILE).sh -it biidinwebapimigrations python manage.py makemigrations

docker_migrate: docker_build
	docker run --env-file ./scripts/$(TARGET_ENV_FILE).sh -it biidinwebapimigrations python manage.py migrate



upgrade: #https://stackoverflow.com/questions/24764549/upgrade-python-packages-from-requirements-txt-using-pip-command
	pip-upgrade

lock:
	pip freeze > requirements.txt