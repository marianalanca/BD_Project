from python:3.9-alpine

RUN apk update && apk add postgresql-dev gcc python3-dev musl-dev

run pip install flask

run pip install pyjwt

run pip install psycopg2-binary

copy . /app

volume ["/app"]

workdir /app

run mkdir -p logs

EXPOSE 5000

CMD ["python", "auctionAPI.py"]
