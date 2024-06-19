# This file outputs data from the database
# The output data is useful for connecting to the database

output "address" {
  value = aws_db_instance.database.address
}

output "port" {
  value = aws_db_instance.database.port
}

output "db_name" {
  value = aws_db_instance.database.db_name
}

output "host" {
  value = aws_db_instance.database.username
}