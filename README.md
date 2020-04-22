# What is it?
An online website for repair shops of smartphones.

# Setup
## Getting Started

Create and activate a virtual environment, and then install the requirements.

```sh
$ virtualenv venv && source venv/bin/activate
$ pip install -r requirements.txt
```

### Set Environment Variables

Update *project/server/config.py*.
By default the app is set to use the production configuration. If you would like to use the development configuration, you can alter the `APP_SETTINGS` environment variable:

**PRO TIP**: Store all env vars inside a .env file, so that you dont have to set them all the time.
```sh
$ export APP_SETTINGS=project.server.config.DevelopmentConfig
```

You can set the `TRICOMA_API_URL` if you want to use the API to create customers.

### Create DB
At first you need to create a new local postgres database:
```postgresql
create database "pricepicker-v2";
create user "some user" with encrypted password 'some password';
grant all privileges on database "pricepicker-v2" to "some user";
```

Then you just need to update the `DATABASE_URL`:
```sh
$ export DATABASE_URL=postgresql://picker:#@127.0.0.1/pricepicker-v2
```

```sh
$ python manage.py create-db
$ python manage.py db init
$ python manage.py db migrate
$ python manage.py create-admin
$ python manage.py create-data
```

### Run the Application

```sh
$ python manage.py run
```

Access the application at the address [http://localhost:5000/](http://localhost:5000/)

### Testing

Without coverage:

```sh
$ python manage.py test
```

With coverage:

```sh
$ python manage.py cov
```

Run flake8 on the app:

```sh
$ python manage.py flake
```

or

```sh
$ flake8 project
```
