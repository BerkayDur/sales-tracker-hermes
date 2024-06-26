# Hermes Sales Tracker Dashboard

This repository contains the files required to run the Hermes Sales Tracker dashboard. The dashboard is built using Streamlit and Docker for easy deployment.

## Folders and Files

### Folders


| Name                 | Description                                               |
|----------------------|-----------------------------------------------------------|
| **`pages`**          | Contains the different pages that the dashboard uses.     |
| **`utilities`**      | Contains scripts for completing various tasks.            |
| **`login.py`**       | Code used for logging the user into the dashboard.        |
| **`navigation.py`**  | Code used for navigating through the dashboard.           |
| **`requirements.txt`** | Lists the required libraries for running the code.      |
| **`README.md`**      | This file, providing an overview and instructions.        |


## Setup Instructions

### Prerequisites

- Python 3.x
- Docker
- Streamlit

### Installing Dependencies

First, ensure you have all required libraries installed. You can install them using the following command:

```bash
pip install -r requirements.txt
```

### Running the Dashboard Locally

To run the dashboard locally, you can use the following command:

```bash
streamlit run login.py
```

### Docker Instructions

#### Building the Docker Image

To build the Docker image, use the following command:

```bash
docker build --platform linux/amd64 -t c11-hermes-dashboard .
```

#### Running the Docker Container

To run the Docker container, use the following command:

```bash
docker run --platform linux/amd64 --env-file .env -p 8501:8501 c11-hermes-dashboard:latest
```

#### Tagging the Docker Image

To tag the Docker image for pushing to your repository, use the following command:

```bash
docker tag c11-hermes-dashboard:latest <your_ecr_repository>:latest
```

#### Pushing the Docker Image

To push the Docker image to your repository, use the following command:

```bash
docker push <your_ecr_repository>:latest
```

Replace `<your_ecr_repository>` with your actual Amazon ECR repository URI.

## Environment Variables

The application uses environment variables for configuration. Make sure to create a `.env` file in the root directory of your project and include all necessary environment variables.


| Variable            | Description                                           |
|---------------------|-------------------------------------------------------|
| ACCESS_KEY          | Your AWS access key                                   |
| SECRET_ACCESS_KEY   | Your AWS secret access key                            |
| AWS_REGION_NAME     | The AWS region name where your services are hosted    |
| DB_USER             | Username for your database                            |
| DB_PASSWORD         | Password for your database                            |
| DB_HOST             | Host address for your database                        |
| DB_PORT             | Port number for your database                         |
| DB_NAME             | Name of your database                                 |

