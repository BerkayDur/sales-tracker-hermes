FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY extract_from_asos.py .
COPY extract_combined.py .

CMD [ "extract_combined.handler" ]