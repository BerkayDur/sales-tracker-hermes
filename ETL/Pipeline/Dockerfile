FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY pipeline_helpers.py .
COPY extract_asos.py .
COPY extract_patagonia.py .
COPY extract_main.py .

CMD [ "extract_main.handler" ]