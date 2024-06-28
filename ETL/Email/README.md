# Email Lambda

This folder contains the scripts and Infrastructure as Code (IaC) necessary for the Lambda function responsible for the final load process. It includes sending email alerts to users using Amazon Simple Email Service (SES) when there are price reductions. Below is a detailed description of each file and its purpose:

## Files

| **File/Directory**        | **Description**                                                                                   |
|---------------------------|---------------------------------------------------------------------------------------------------|
| `combined_load.py`        | Contains the logic for combining data and triggering email alerts based on price reductions.     |
| `conftest.py`             | Configuration file for pytest to define fixtures and settings.                                    |
| `Dockerfile`              | Defines the Docker image used for building and deploying the Lambda function.                    |
| `email_helpers.py`        | Includes helper functions for formatting and preparing email content.                            |
| `email_service.py`        | Interfaces with Amazon SES to send emails to users.                                               |
| `handler.py`              | Entry point for the Lambda function, orchestrating the load process and email notifications.     |
| `README.md`               | Provides an overview and instructions for the project.                                            |
| `requirements.txt`        | Lists the Python dependencies required for the project.                                           |
| `Terraform`               | Directory containing Terraform scripts for deploying the Lambda function and related resources.  |
| `test_combined_load.py`   | Unit tests for `combined_load.py`.                                                                |
| `test_email_helpers.py`   | Unit tests for `email_helpers.py`.                                                                |
| `test_email_service.py`   | Unit tests for `email_service.py`.                                                                |


## Deployment

**Deploy with Terraform:**
If you need to create this infrastructure separately from the ETL process:
```sh
cd Terraform
terraform init
terraform apply
```

**Note:** The ETL process already includes the necessary infrastructure, there is no need to deploy the Terraform scripts in this folder separately unless investigating the email lambda specifically.

## Setting Up a Virtual Environment and Installing Requirements

To set up a virtual environment and install the necessary Python dependencies, follow these steps:

1. **Create a Virtual Environment:**
   ```sh
   python -m venv venv
   ```

2. **Activate the Virtual Environment:**
   - On Windows:
     ```sh
     venv\Scripts\activate
     ```
   - On macOS and Linux:
     ```sh
     source venv/bin/activate
     ```

3. **Install the Requirements:**
   ```sh
   pip install -r requirements.txt
   ```

## Running Tests

To run the tests, use pytest:

```sh
pytest
```

## Usage

The Lambda function can be invoked manually or automatically based on triggers defined in the Terraform scripts. It will process the data, detect price reductions, and send email notifications to users via Amazon SES.