FROM python:3.11-slim as builder


ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app


RUN apt-get update && apt-get install -y --no-install-recommends gcc python3-dev \
    && rm -rf /var/lib/apt/lists/*


RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"


COPY requirements.txt .
RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt


FROM python:3.11-slim as runtime


RUN groupadd -r django && useradd -r -g django django

WORKDIR /app
COPY --from=builder /opt/venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1


COPY . /app/


RUN chown -R django:django /app


USER django

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]