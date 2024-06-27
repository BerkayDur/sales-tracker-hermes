# ETL Pipeline

The Extract, Transform, Load (ETL) pipeline is designed for updating product price data regularly and allowing for extensive upscaling without compromising performance.

## Folder Structure

| Folder        | Description |
|---------------|-------------|
| **Email**     | Contains the Lambda function script responsible for the final load process, sending email alerts to users using Amazon Simple Email Service (SES) when there are price reductions. |
| **Pipeline**  | Includes the scripts and configurations that define the overall ETL pipeline, managing the coordination between the extract, transform, and load processes. |
| **Provision** | Contains the Lambda function responsible for the extraction process. This function extracts data from the RDS database and groups it into manageable chunks for the transform Lambdas. |
| **Step-Function** | Houses the AWS Step Functions definitions that orchestrate the ETL process, ensuring the correct sequence of execution and handling retries and error handling. |
| **Terraform** | Contains the infrastructure as code scripts used to provision and manage the AWS resources required for the ETL pipeline, ensuring consistent and repeatable deployment. |

## Detailed Process Overview

### Extract

- **Provisioning Lambda**: This Lambda function is responsible for extracting data from the RDS database. It groups the extracted data into manageable chunks, each to be processed by separate transform Lambdas. This design ensures efficient scraping of price data, regardless of the number of products being tracked.

### Transform

- **Transform Lambda**: The data extracted by the Provisioning Lambda is processed and filtered within these Lambdas. Only details of products that have decreased in price are sent forward to the load process.

### Load

- **Email Lambda**: This script utilizes Amazon Simple Email Service (SES) to send email alerts to users when there are price reductions for the products they are tracking.