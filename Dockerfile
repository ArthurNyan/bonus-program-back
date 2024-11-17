FROM python:3.9

WORKDIR /app

RUN pip install --no-cache-dir poetry

COPY pyproject.toml poetry.lock ./

RUN poetry config virtualenvs.create false && poetry install --no-root --no-dev

COPY . .

EXPOSE 5002

CMD ["python", "app.py"]
