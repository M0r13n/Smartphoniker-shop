# What is it?
An online website for repair shops of smartphones.

# Setup
## Getting Started


### Docker (recommended)

Build the application with `docker-compose` (the first build can take some time):

```sh
$ make docker-build
```

Run development server:

```sh
$ make docker-dev
```

Run production server:

```sh
$ make docker-prod
```

After you started the container you need to initialize the database:

```sh
$ docker-compose exec <YOUR_SERVER_TYPE> make db
```

where you need to replace `<YOUR_SERVER_TYPE>` with either `pricepicker-prod` or `pricepicker-dev`.



Run tests:

```sh
$ make docker-test
```

Execute command inside docker container. E.G. add sample data to your local dev server:

```sh
$ docker-compose exec pricepicker-dev make db
```

### Without Docker (not recommended)

Create and activate a virtual environment, and then install the requirements.

```sh
$ virtualenv venv && source venv/bin/activate
$ make install
```

### Set Environment Variables

Update *project/server/config.py*.
By default the app is set to use the production configuration. If you would like to use the development configuration, you can alter the `APP_SETTINGS` environment variable:

**PRO TIP**: Store all env vars inside a `.local_env` file, so that you dont have to set them all the time.

**DO NOT CREATE A `.env` file for your local dev env, because this file may be used inside docker!**

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