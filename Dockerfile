FROM python:3

WORKDIR /app

COPY . .

CMD [ "python", "./server3.py" ]
