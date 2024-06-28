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

### Setup 

1. **Create `terraform.tfvars` File**:
   Within the `Terraform` directory, create a `terraform.tfvars` file and provide the necessary values for the variables in `variables.tf`. E.g.:
   ```hcl
   PROCESSING_BATCH_SIZE = "Your desired batch size"
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

4. **Retrieve Outputs**:
   After the `apply` step completes, Terraform will output the necessary information to connect to your database. You can also use:
   ```sh
   terraform output
   ```


### Cleaning Up

To destroy the RDS instance and clean up the resources created by Terraform, run:
```sh
terraform destroy
```
Review the planned actions and confirm by typing `yes`.

### Support

For any issues or questions, please refer to the [Terraform AWS Provider Documentation](https://registry.terraform.io/providers/hashicorp/aws/latest/docs) or contact the project maintainer.

---

By following the above steps, you will successfully set up a PostgreSQL database on AWS RDS using Terraform.
