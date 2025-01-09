FROM python:3.11
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
WORKDIR ./app
RUN python -m pip install --upgrade pip
COPY requirements.txt /app/
RUN pip install -r requirements.txt
COPY ./ketoApp/ .



