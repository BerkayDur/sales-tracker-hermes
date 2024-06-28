# Pipeline Lambda

This folder contains the scripts and Infrastructure as Code (IaC) necessary for the Lambda functions responsible for the data extraction and transform processes. It includes extracting data from various sources and using helper functions to streamline the pipeline. Below is a detailed description of each file and its purpose:

## Files

| **File/Directory**        | **Description**                                                                                   |
|---------------------------|---------------------------------------------------------------------------------------------------|
| `__pycache__`             | Directory containing Python bytecode files.                                                       |
| `conftest.py`             | Configuration file for pytest to define fixtures and settings.                                    |
| `Dockerfile`              | Defines the Docker image used for building and deploying the Lambda function.                    |
| `extract_asos.py`         | Contains the logic for extracting data from ASOS.                                                 |
| `extract_main.py`         | Main script orchestrating the data extraction from all sources.                                   |
| `extract_patagonia.py`    | Contains the logic for extracting data from Patagonia.                                            |
| `pipeline_helpers.py`     | Includes helper functions for the data extraction pipeline.                                       |
| `README.md`               | Provides an overview and instructions for the project.                                            |
| `requirements.txt`        | Lists the Python dependencies required for the project.                                           |
| `Terraform`               | Directory containing Terraform scripts for deploying the Lambda function and related resources.  |
| `test_extract_asos.py`    | Unit tests for `extract_asos.py`.                                                                 |
| `test_extract_main.py`    | Unit tests for `extract_main.py`.                                                                 |
| `test_extract.py`         | Unit tests for common extraction logic.                                                           |
| `test_pipeline_helpers.py`| Unit tests for `pipeline_helpers.py`.                                                             |


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

The Lambda function can be invoked manually or automatically based on triggers defined in the Terraform scripts. It will extract data from the specified sources and use helper functions to process the data as needed.