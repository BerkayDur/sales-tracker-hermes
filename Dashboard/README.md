# Dashboard


## Folders

| Folder | Description |
|---|---|
| **pages** | Containing the different paged that the dashboard uses. |
| **utilities** | The scripts for completing the tasks that the dashboard requires. |
| **login.py** | Code used for logging the user into the dashboard. |
| **navigation.py**  | The code used for navigating the dashboard. |
| **requirements.txt** | Contains the required libraries for running the code. |
| **README.md**  | This file. |

streamlit run login.py
docker build --platform linux/amd64 -t c11-hermes-dashboard .
docker run --platform linux/amd64 --env-file .env -p 8501:8501 c11-hermes-dashboard:latest
docker tag c11-hermes-dashboard:latest <your_ecr_repository>:latest
docker push <your_ecr_repository>latest