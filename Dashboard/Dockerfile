FROM python:latest

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY login.py .
COPY navigation.py .
COPY .streamlit/config.toml .
COPY utilities/email_verification.py .
COPY utilities/ses_get_emails.py .
COPY pages/price.py .

EXPOSE 80

CMD [ "streamlit", "run", "login.py" ]