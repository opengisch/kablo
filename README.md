# kablo: Open Source for Electric Network Information System

POC: Open Source for Electric Network Information System

⚠️ THIS IS ***NOT*** READY FOR PRODUCTION ⚠️

## Setting up full Docker non persistent demo

This will bring up a demo instance served by the
Django development server in reload mode.

```bash
git clone git@github.com:yverdon/kablo.git && cd kablo
# copy default config
cp -n .env.example .env
# start the stack
docker compose up --build -d --remove-orphans
# run the migrations
docker compose run kablo scripts/migrate.sh
```

As fixtures are not yet available, should you need and superadmin account, please create it as follow: ```python manage.py createsuperuser```

If everything went fine, go to ```localhost:9051``` and you should see the welcome page:


## Setting up production instance

### Database

1. Create a PostgreSQL database.
2. Install required extensions:

```sql
CREATE EXTENSION postgis;
```

3. Edit DB connection in `.env` file

### Environment variables

:warning: :warning: :warning:

Set the following variables as follow:

```ini
COMPOSE_FILE=docker-compose.yml
```

And review all other variables in order to fine tune your instance

### Deploying changes

New changes are deployed with the following command. :warning: **WARNING**: on PROD, docker-compose up will automatically
run migrations, collect static files, compile messages and update integrator permissions in the entrypoint.

```bash
# update the stack
docker compose up --build -d --remove-orphans
```

## Contribution guideline

? Use [Gitflow](https://www.atlassian.com/fr/git/tutorials/comparing-workflows/gitflow-workflow) to contribute to the project. ?

## Development tools

### Run the tests from within the docker container

Run tests in a the running container:

```bash
docker compose exec web python manage.py test --settings=kablo.settings_test
```

Run a specific test in the running container (adding the `--keepdb` flag speeds up iterations):

```bash
docker compose exec web python manage.py test --settings=kablo.settings_test --keepdb kablo.apps.permits.tests.test_a_kablo_case
```

### Linting

We use [pre-commit](https://pre-commit.com/) as code formatter. Just use the following command to automatically format your code when you commit:

```
$ pip install pre-commit
$ pre-commit install
```

If you wish to run it on all files:

```
$ pre-commit run --all-files
```

### Dependency management

Dependencies are managed with [`pip-tools`](https://github.com/jazzband/pip-tools).

### Installing packages

To install a new package, add it to `requirements.in`, without pinning it to a
specific version unless needed. Then run:

```
docker compose exec kablo pip-compile requirements.in
docker compose exec kablo pip-compile requirements_dev.in
docker compose exec kablo pip install -r requirements.txt
docker compose exec kablo pip install -r requirements_dev.txt
```

Make sure you commit both the `requirements.in` and the `requirements.txt` files.
And the `requirements_dev.in` and the `requirements_dev.txt` files.

### Upgrading packages

To upgrade all the packages to their latest available version, run:

```
docker compose exec kablo pip-compile -U requirements.in
docker compose exec kablo pip install -r requirements.txt
```

To upgrade only a specific package, use `pip-compile -P <packagename>`.
The following commands will upgrade Django to its latest version, making sure
it's compatible with other packages listed in the `requirements.in` file:

```
docker compose exec web pip-compile -P django requirements.in
docker compose exec web pip install -r requirements.txt
```

## Documenting models

In order to generate the model documentation, run:
```
docker compose run kablo scripts/generate_models_diagram.sh
```

### Two factor authentication [NOT IMPLEMENTED]

You can enable 2FA by setting the variable `ENABLE_2FA` to `true`. Defaults to `false`.

### Access to admin views under 2FA

Super users require to enable 2FA to have access to the admin app.

Follow the following steps:

1. Go to the `/account/login/` and sign in with your super user credentials
2. Follow the steps to activate 2FA
3. Open `/admin/`

Next time you sign in, you will be asked for a token.
Once you provided your token go to `/admin/` to access the admin app.

### kablo as a OAuth2 provider [NOT IMPLEMENTED]
* [Access to a ressources with QGIS](docs/OAuth2_Qgis.md)
* [Access to a ressources with a bearer token](docs/OAuth2_access_api.md)
