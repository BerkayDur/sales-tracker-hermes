streamlit run login.py
docker build --platform linux/amd64 -t c11-hermes-dashboard .
docker run --platform linux/amd64 --env-file .env -p 8501:8501 c11-hermes-dashboard:latest
docker tag c11-hermes-dashboard:latest <your_ecr_repository>:latest
docker push <your_ecr_repository>latest