# Recipe APP API Project V2

DOCKERIZING AN APP
Create a docker file: Dockerfile Build a docker project

```
make build
```

Create docker compose yaml file: docker-compose.yml

Build a docker project with docker-compose

```
make start
```

Create a django project with docker-compose

```
docker-compose run --rm app sh -c "django-admin startproject project_name ."
```

create a django application in django project with docker-compose

```
make startapp APP=app_name
```

Make application migrations with docker-compose

```
make makemigrations
```

Start development server

```
make start
```

Create admin user

```
make createsuperuser
```

Interract with database

```
docker-compose run --rm app sh -c "python manage.py dbshell"
```

Testing the application

Running tests and linting

```
make lint
make quality_checks
make test
```

## Deployment SetUp with AWS EC2

Find more instruction details [here](https://github.com/PatrickCmd/build-a-backend-rest-api-with-python-django-advanced-resources/blob/main/deployment.md)
