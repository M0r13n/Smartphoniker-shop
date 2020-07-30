# What is it?
An online website for repair shops of smartphones.

# Setup
## Getting Started

Create and activate a virtual environment, and then install the requirements.

```sh
$ virtualenv venv && source venv/bin/activate
$ make install
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
$ export DATABASE_URL=postgresql://<YOUR_URL>:#@127.0.0.1/<YOUR_DB>
```

```sh
$ make db
```

### Run the Application

```sh
$ make run
```

Access the application at the address [http://localhost:5000/](http://localhost:5000/)

### Start Celery
If you want to start the celery worker, you need to have Redis running somewhere. 
Change the `REDIS_URL` accordingly inside your `config.py` or `.env`.
You can start a celery worker by calling:

```sh
$ python manage.py start-worker [loglevel]
```

### Testing

Without coverage:

```sh
$ make test
```