# A bash script to query the database using the queries in the queries.sql file

source .env
export PGPASSWORD=$DB_PASSWORD
psql --host $DB_HOST -U $DB_USER -p $DB_PORT $DB_NAME -f query.sql