FROM python:3

RUN apt-get update
RUN apt-get install -y libgdal-dev

# Only requirements.txt file, so we can leverage cache later and save big time.
RUN pip install -U pip

WORKDIR /code
COPY ./requirements.txt /code/requirements.txt
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

# Then the app.
COPY ./app /code/app
COPY ./.env /code/.env
ENV PYTHONPATH=/code/app

# Entrypoint.
CMD ["uvicorn", "app.simple_api:app", "--host", "0.0.0.0", "--port", "80"]