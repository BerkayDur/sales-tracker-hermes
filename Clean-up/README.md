# Clean-up

This directory contains the necessary scripts and configurations for cleaning up unsubscribed products from the database.

## Contents

- `.env`: Environment variables configuration file.
- `clean_lambda.py`: Python script for the AWS Lambda function that performs the clean-up operation.
- `Dockerfile`: Docker configuration for containerizing the Lambda function.
- `requirements.txt`: Python dependencies for the clean-up script.
- `test_clean_lambda.py`: Unit tests for the clean-up Lambda function.
- `Terraform/`: Directory containing Terraform configurations to deploy the Lambda function and its associated resources.

## Environment Variables

The `.env` file should contain the following variables:

```
DB_USER=your_database_user
DB_PASSWORD=your_database_password
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_NAME=your_database_name
```

## clean_lambda.py

This script connects to the PostgreSQL database and deletes products that are not subscribed. The main function, `handler`, is designed to be triggered by AWS Lambda.

### Key Functions

- `get_connection()`: Establishes a connection with the PostgreSQL database.
- `get_cursor(conn)`: Returns a cursor for executing database queries.
- `delete_unsubscribed(conn, table)`: Deletes unsubscribed products from the specified table.
- `handler(_event, _context)`: The main Lambda handler function that performs the clean-up operation.

## Dockerfile

The Dockerfile is used to create a Docker image for the clean-up Lambda function. It installs the necessary dependencies and sets the `clean_lambda.handler` as the entry point.

### Build and Push Docker Image to AWS ECR

```sh
# Build Docker image
docker build --platform linux/amd64 -t clean-lambda .

# Tag the Docker image
docker tag clean-lambda:latest <your_ecr_repository>:latest

# Push Docker image to ECR
docker push <your_ecr_repository>:latest
```

### Build and Push Docker Image locally

```sh
# Build Docker image
docker build --platform linux/amd64 -t c11-hermes-clean .

# Run Docker image locally
docker run --platform linux/amd64 --env-file .env -p 9000:8080 c11-hermes-clean:latest

# On another terminal run :
curl "http://localhost:9000/2015-03-31/functions/function/invocations" -d "{}"
```

## requirements.txt

This file lists the Python dependencies required by the clean-up script.

## test_clean_lambda.py

This file contains unit tests for the clean-up script to ensure its correctness. It uses `pytest` for testing. Enter the following command in the terminal to run the test:

```sh
pytest test_clean_lambda.py
```

## Terraform

The `Terraform/` directory contains the Terraform configurations for deploying the Lambda function and the EventBridge rule to AWS.

### Files

- `main.tf`: Main Terraform configuration file for Lambda and EventBridge.
- `outputs.tf`: Outputs information about the deployed lambda including ARN and name.
- `terraform.tfvars`: Variable values for Terraform configuration.
- `variables.tf`: Variable definitions for Terraform.

## Environment Variables

The `terraform.tfvars` file should contain the following variables:

```hcl
DB_HOST="your_database_host"
DB_NAME="your_database_name"
DB_PASSWORD="your_database_password"
DB_PORT=your_database_port
DB_USER="your_database_user"
```

### Usage

```sh
# Initialize Terraform
terraform init

# Apply Terraform configurations
terraform apply
```

Ensure you have AWS credentials configured and Terraform installed before running the commands.

## Summary

This directory provides all the necessary components to deploy an automated clean-up process for unsubscribed products using AWS Lambda, Docker, and Terraform.