## Provision Overview
This is the script to read the product URLs, Prices and IDs from the database, and output this in batches suitable for provisioning further lambdas.

## Files

### `provision_lambda.py`
- Connects to a PostgreSQL database, retrieves product data, and organizes it into batches.
- **Key Functions**:
  - `get_connection(config)`: Connects to the database.
  - `read_database(conn)`: Retrieves product data.
  - `group_data(data, size)`: Groups data into batches.
  - `handler(event, context)`: Lambda handler function.

### `Dockerfile`
- Builds a Docker image for the Lambda function.
- **Commands**:
  - Install dependencies.
  - Copy the script.
  - Set the Lambda handler.

### `requirements.txt`
- **Dependencies**:
  - `psycopg2-binary`
  - `python-dotenv`

### `test_provision_lambda.py`
- Unit tests for `group_data` and `read_database`.


## Environment Variables


Create a file named `.env` in the Provision folder. 
Populate it with the following details:

```env
DB_HOST=your_database_host
DB_PORT=your_database_port
DB_NAME=your_database_name
DB_USER=your_database_user
DB_PASSWORD=your_database_password
PROCESSING_BATCH_SIZE=desired_lambda_batch_size
```