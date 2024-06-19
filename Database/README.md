## Terraform Configuration for AWS RDS PostgreSQL Database

This project provides Terraform configuration files to set up and manage a PostgreSQL database instance on Amazon RDS (Relational Database Service). The configuration includes creating the database instance and outputting necessary connection information.

### Prerequisites

- Terraform installed on your local machine.
- AWS account credentials configured. You can configure AWS credentials by running `aws configure` in your terminal or setting environment variables (`AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY`).
- Basic knowledge of Terraform and AWS.

### Files Overview

1. **main.tf**: The main Terraform configuration file that defines the AWS RDS PostgreSQL database instance.
2. **outputs.tf**: This file outputs important information about the database instance, which is useful for connecting to the database.
3. **variables.tf**: This file defines variables used in the Terraform configuration and assigns default values where applicable.
4. **terraform.tfvars**: This file should be created by the user to provide values for the variables defined in `variables.tf`.

### main.tf

This file contains the primary configuration for the AWS RDS PostgreSQL database instance.

- The `terraform` block specifies the required provider (AWS) and its version.
- The `provider` block sets the AWS region, which is defined by the `AWS_REGION` variable.
- The `aws_db_instance` resource defines the configuration for the RDS instance, including allocated storage, database name, availability zone, engine type, instance class, security groups, and other settings.

### outputs.tf

This file defines outputs that provide essential information about the RDS instance:

- `address`: The DNS address of the RDS instance.
- `port`: The port number on which the database is listening.
- `db_name`: The name of the database.
- `host`: The master username for the database.

### variables.tf

This file defines the variables used in the Terraform configuration:

- `AWS_REGION`: The AWS region where the RDS instance will be created. Default is `eu-west-2`.
- `DB_PASSWORD`: The password for the PostgreSQL database.

### Instructions

1. **Clone the Repository**:
   ```sh
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create `terraform.tfvars` File**:
   Create a `terraform.tfvars` file in the same directory and provide the necessary values for the variables:
   ```hcl
   DB_PASSWORD = "your_db_password"
   ```

3. **Initialize Terraform**:
   Initialize the Terraform configuration by running:
   ```sh
   terraform init
   ```

4. **Apply Terraform Configuration**:
   Apply the Terraform configuration to create the RDS instance:
   ```sh
   terraform apply
   ```

   Review the planned actions and confirm by typing `yes`.

5. **Retrieve Outputs**:
   After the `apply` step completes, Terraform will output the necessary information to connect to your database. You can also use:
   ```sh
   terraform output
   ```

### Security Considerations

- Ensure your `DB_PASSWORD` is stored securely and not hardcoded in the Terraform files.
- Use appropriate security group settings to restrict access to your RDS instance.
- Enable encryption for data at rest and in transit.

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

# Database Setup

## Prerequisites

- PostgreSQL installed on your system.
- Access to a PostgreSQL database.
- Bash shell environment.


### Create a `.env` File

Create a file named `.env` in the database folder. 
Populate it with the following details:

```env
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
```

Replace the placeholders with your actual database connection details.


### Connecting to the Database

To connect to your database, run the `connect.sh` script.

```bash
bash connect.sh
```

This script will load the environment variables and connect you directly to the PostgreSQL database interactive terminal.

### Querying the Database

To run predefined queries on the database, first create the queries in the `query.sql` file, for example: 
```sql
SELECT * FROM price_readings;
```
Then run the `query.sh` script to run it:

```bash
bash query.sh
```

