FROM python:3.8.2
WORKDIR /home

EXPOSE 8000

RUN mkdir -p /home/db

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .
COPY db.sqlite3 ./

RUN python manage.py migrate

#RUN python manage.py createsuperuser

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]