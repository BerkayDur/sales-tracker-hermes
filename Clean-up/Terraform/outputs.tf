# This file outputs information about the labda function

output "lambda_name" {
  value = aws_lambda_function.c11-hermes-clean_lambda.function_name
}

output "lambda_arn" {
  value = aws_lambda_function.c11-hermes-clean_lambda.arn
}