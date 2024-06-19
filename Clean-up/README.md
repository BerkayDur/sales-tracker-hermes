docker build --platform linux/amd64 -t c11-hermes-clean .
docker run --platform linux/amd64 --env-file .env -p 9000:8080 c11-hermes-clean:latest
on another terminal run:
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d '{}'

https://docs.aws.amazon.com/lambda/latest/dg/python-image.html