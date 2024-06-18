# This file outputs data from the database
# The output data is useful for connecting to the database

data "aws_db_instance" "database" {
  db_instance_identifier = "c11-hermes-db"
}

output "address" {
  value = data.aws_db_instance.database.address
}

output "port" {
  value = data.aws_db_instance.database.port
}

output "db_name" {
  value = data.aws_db_instance.database.db_name
}

output "host" {
  value = data.aws_db_instance.database.master_username
}