build:
	docker-compose build

start:
	docker-compose up -d

down:
	docker-compose down

app-logs:
	docker-compose logs -f app

makemigrations:
	docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py makemigrations"

migrate:
	docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py migrate"

startapp:
	docker-compose run --rm app sh -c "python manage.py startapp ${APP}"

test:
	docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py test"

createsuperuser:
	docker-compose run --rm app sh -c "python manage.py wait_for_db && python manage.py createsuperuser"

remove-volume:
	docker volume rm recipe-app-api-v2_dev-db-data

lint:
	docker-compose run --rm app sh -c "black --exclude=migrations ."
	docker-compose run --rm app sh -c "isort ./*/*.py"
	docker-compose run --rm app sh -c "flake8"

quality_checks:
	docker-compose run --rm app sh -c "flake8"
	docker-compose run --rm app sh -c "black --check --exclude=migrations ."
	docker-compose run --rm app sh -c "isort ./*/*.py --check-only"

gs:
	git status

make gadd:
	git add .

make gcommit:
	git commit -am "${MESSAGE}"

make gpush:
	git push -u origin ${BRANCH}
