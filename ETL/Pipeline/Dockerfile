FROM public.ecr.aws/lambda/python:3.12

WORKDIR ${LAMBDA_TASK_ROOT}

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY extract_asos.py .
COPY extract_main.py .
COPY extract_patagonia.py .
COPY pipeline_helpers.py .

CMD [ "extract_main.handler" ]