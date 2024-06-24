FROM python:latest

RUN mkdir .streamlit
RUN mkdir utilities
RUN mkdir pages

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY login.py .
COPY navigation.py .
COPY .streamlit/config.toml .streamlit
COPY utilities/email_verification.py utilities
COPY utilities/ses_get_emails.py utilities
COPY pages/price.py pages

EXPOSE 8501

CMD [ "streamlit", "run", "login.py", "--server.port=8501", "--server.address=0.0.0.0" ]