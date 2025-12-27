include ./scripts/env.sh
TARGET_ENV_FILE=env_docker

workspace:
	python3 -m venv env
	source env/bin/activate
	python3 -m pip install -r requirements.txt


start:
	python manage.py collectstatic;
	./env/bin/gunicorn config.asgi -k config.my_uvicorn_worker.MyUvicornWorker --bind="0.0.0.0:${PORT}"  --timeout ${SERVER_TIMEOUT} --log-level=debug --threads 8;

port_grep:
	lsof -i |grep :9896

docker_build:
	docker build -t biidinwebapi .

docker: docker_build
	docker run --env-file ./scripts/$(TARGET_ENV_FILE).sh -it -p 9896:9896 biidinwebapi

collectstatic:
	bash -c "source ./scripts/env.sh && python manage.py collectstatic"

encrypt:
	ANSIBLE_VAULT_PASSWORD_FILE=${PWD}/.vault_password.txt ansible-vault encrypt ${PWD}/scripts/env_docker.sh

decrypt:
	ANSIBLE_VAULT_PASSWORD_FILE=${PWD}/.vault_password.txt ansible-vault decrypt ${PWD}/scripts/env_docker.sh

helm:
	helm package --app-version=latest helm/biidinwebapi
	helm upgrade --install biidinwebapi -f helm/biidinwebapi/values.io.yaml ./biidinwebapi-0.1.0.tgz  --namespace io

test:
	curl -H "X-API-Key: 123456wer12wegfqwtg24t2462f" "http://localhost:9896/api/language_to_sql?text_query=get+me+10+&table_name=tvl"



mysql_demo_flights_routes:
	bash -c "source ./scripts/env.sh && python3 poc/mysql_demo_flights_routes/main.py"

mysql_demo_bank_churners:
	bash -c "source ./scripts/env.sh && python3 poc/mysql_demo_bank_churners/main.py"

mysql_demo_customer_address:
	bash -c "source ./scripts/env.sh && python3 poc/mysql_demo_customer_address/main.py"

mysql_demo_incident_report_fraud:
	bash -c "source ./scripts/env.sh && python3 poc/mysql_demo_incident_report_fraud/main.py"


docker_create_main_api_key: docker_build
	docker run  --env SERVER_ROLE=  --env-file ./scripts/$(TARGET_ENV_FILE).sh -it \
		biidinwebapi python manage.py create_main_api_key -key 3cdbee7ad3d6283bc7dfdf97782ffb475bdf24f2267dfcc32b42f65b95323de9


.PHONY: workspace docker_build docker encrypt decrypt helm


pip_show_version:
	pip show langchain llama-index