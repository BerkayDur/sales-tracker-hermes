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

COPY email_verification.py .
COPY extract_combined.py .
COPY extract_from_asos.py .
COPY extract_from_patagonia.py .
COPY uhelpers.py .
COPY load.py .
COPY ses_get_emails.py .

COPY login.py .
COPY navigation.py .

EXPOSE 8501

CMD [ "streamlit", "run", "login.py", "--server.port=8501", "--server.address=0.0.0.0" ]