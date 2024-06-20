# This file outputs information about the lambda function

output "lambda_name" {
  value = aws_lambda_function.provision_lambda.function_name
}

output "lambda_arn" {
  value = aws_lambda_function.provision_lambda.arn
}