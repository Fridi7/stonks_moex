FROM python:3.7
ENV PYTHONUNBUFFERED 1
RUN mkdir /app
WORKDIR /app
COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

RUN python app/manage.py makemigrations stonks
RUN python app/manage.py migrate
CMD ["python", "app/manage.py", "runserver", "0.0.0.0:8000"]