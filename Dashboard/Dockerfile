FROM python:latest

COPY requirements.txt .
RUN pip install -r requirements.txt

RUN mkdir .streamlit
COPY .streamlit/config.toml .streamlit

RUN mkdir logo
COPY logo/hermes_crop.png logo
COPY logo/hermes_logo_full.png logo
COPY logo/hermes_logo.png logo

RUN mkdir pages
COPY pages/email_alerts.py pages
COPY pages/price.py pages

RUN mkdir utilities
COPY utilities/email_verification.py utilities
COPY utilities/extract_combined.py utilities
COPY utilities/extract_from_asos.py utilities
COPY utilities/extract_from_patagonia.py utilities
COPY utilities/helpers.py utilities
COPY utilities/load.py utilities
COPY utilities/ses_get_emails.py utilities

COPY login.py .
COPY navigation.py .

EXPOSE 8501

CMD [ "streamlit", "run", "login.py", "--server.port=8501", "--server.address=0.0.0.0" ]