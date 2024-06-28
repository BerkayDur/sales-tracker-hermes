# Hermes Sales Tracker Dashboard

This repository contains the files required to run the Hermes Sales Tracker dashboard. The dashboard is built using Streamlit and Docker for easy deployment.

## Folders and Files

### Folders


| Name                 | Description                                               |
|----------------------|-----------------------------------------------------------|
| **`pages`**          | Contains the different pages that the dashboard uses.     |
| **`login.py`**       | Code used for logging the user into the dashboard.        |
| **`navigation.py`**  | Code used for navigating through the dashboard.           |
| **`test_...py`**| Contains Pytests for named files.|
| **`custom_styling.py`**| Contains customized CSS styling for the Dashboard.|
| **`email_verification.py`**| Contains the email verification logic.|
| **`extract_from_asos.py`**| Contains the logic to get product information from asos.|
| **`extract_from_patagonia.py`**| Contains the logic to get product information from asos.|
| **`extract_combined.py`**| Contains the logic to get product information (combines all `extract_from_...py` files).|
| **`helpers.py`**| Contains the helpers to that is used throughout this directory.|
| **`load.py`**| Contains the logic to load extracted data from `extract_combined.py` to the database.|
| **`ses_get_email.py`**| Contains the logic to get ses emails.|
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

## Terraform

To host your program on AWS:
1. **Create `terraform.tfvars` File**:
   Within the `Terraform` directory, create a `terraform.tfvars` file and provide the necessary values for the variables in `variables.tf`. E.g.:
   ```hcl
   CLUSTER_ARN = "Your ECS cluster ARN"
   ```

2. **Initialize Terraform**:
   Within the same directory, initialize the Terraform configuration by running:
   ```sh
   terraform init
   ```

3. **Apply Terraform Configuration**:
   Within the same directory, apply the Terraform configuration to create the ETL pipeline infrastructure:
   ```sh
   terraform apply
   ```

   Review the planned actions and confirm by typing `yes`.



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

