all: minify

minify: minify-css minify-js

minify-js:
	curl -X POST -s --data-urlencode 'input@project/client/static/scripts/script.js' https://javascript-minifier.com/raw > project/client/static/scripts/script.min.js

minify-css:
	curl -X POST -s --data-urlencode 'input@project/client/static/css/main.css' https://cssminifier.com/raw > project/client/static/css/main.min.css

test:
	python manage.py test && python manage.py flake

run:
	python manage.py run

install:
	pip install -r ./misc/requirements/requirements_base.txt && pip install -r ./misc/requirements/requirements_dev.txt

db:
	python manage.py create-db && python manage.py db upgrade && python manage.py create-admin && python manage.py create-data

docker-build: docker-down
	docker-compose build --parallel && docker image prune -f

docker-dev:
	docker-compose up pricepicker-dev

docker-prod:
	docker-compose up pricepicker-prod

docker-test:
	docker-compose run --rm pricepicker-test

docker-down:
	docker-compose down
