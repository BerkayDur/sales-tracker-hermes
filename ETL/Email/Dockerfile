FROM public.ecr.aws/lambda/python:latest

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY combined_load.py .
COPY email_helpers.py .
COPY email_service.py .
COPY handler.py .

CMD [ "handler.handler" ]