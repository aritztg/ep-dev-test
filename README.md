# EP Dev Test

![ci workflow](https://github.com/aritztg/ep-dev-test/actions/workflows/code_quality.yml/badge.svg)

## Installation

This guide assumes that the reader has a minimal experience with python and its virtualenvs.

1. Install gdal `$ brew install gdal` or (untested) `$ apt install gdal`.
2. Install a python version (this was tested with 3.11.3): `$ pyenv install 3.11.3`. If `pyenv` is not available in
   your OS, you can use `virtualenv` (`poetry` may require different steps).
3. Create a virtualenv: `$ pyenv virtualenv 3.11.3 earthpulse-simple-api`
4. If not already, now you can start using that environment: `$ pyenv activate earthpulse-simple-api`
5. Install dependences: `$ pip install -r requirements.txt`
6. (Optional) Install dev dependences (for linting and such): `$ pip install -r requirements-dev.txt`
7. Fill credentials in `.env` file. Do not use double quotes or whitespaces.
8. Execute the cli app. `$ python app/simple_api.py` (no params/argparse use yet).

## How to run

### Locally

As a regular python app (in the right environment):
```bash
$ python app/simple_api.py
```

or using makefile entrypoint:

```bash
$ make run
```

Then you should be able to access [http://0.0.0.0:80/docs] and play around with the exposed endpoint. If you prefer,
you can also check docs via [http://0.0.0.0:80/redoc] UI.

### Docker

First build the image (read the file first to understand what it does):
```bash
$ docker build -t earthpulse-simple-api .
```

Then you can run a container based on that image:
```bash
$ docker run -d --name earthpuse-test-container -p 80:80 earthpulse-simple-api
```

## Further development
- Consider the use of pylama for more complete linting.
- Add some FastAPI middlewares, such HTTPSRedirectMiddleware, TrustedHostMiddleware.
- Integrate some logs/app monitor like Sentry or Datadog.
- Using Github actions, check linters and go further (staging/deploy) only if certain threshold has been met (done).

### Linters
Please ensure you have installed development dependences first: `$ pip install -r requirements-dev.txt`.

#### Ruff
Very fast linter, but still does not have the same amount or rules available in pylint. It would be perfect to be used
in a pre-commit Git hook. Uses `pyproject.toml` as configuration file.
```bash
ruff check .
```

#### Pylint
It uses the configuration `pylintrc` settings file. No rules were disabled, AFAIK. It takes more time with larger
codebases. It can be executed locally, and tipically in CD/CI pipelines instead of ruff (because of its large amount
of rules), making the pipeline failing if a minimum threshold score is not reached.
```bash
$ pylint $(find . -name "*.py")

--------------------------------------------------------------------
Your code has been rated at 10.00/10 (previous run: 10.00/10, +0.00)
```

#### Isort
Not exactly a linter, but a useful tool anyway. It ensures some guide styling in regards of module imports.
```bash
$ isort .
```

### Tests
Ensure you install dev-requirements first. Then simply execute:
```bash
$ python -m unittest discover
```

### Makefile
You can run (you need to be in the right virtualenv first):
```bash
make run
make tests
make lint
```

### Github actions
A Github action has been added (`.github/workflows/code_quality.yml`) to check pylint over all py files in the
`main` branch. If linter score is higher than `9`, it could continue to the next ci/cd step (not defined yet).
