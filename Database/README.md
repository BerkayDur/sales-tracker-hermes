
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

