# This file terraforms the provision lambda on AWS

provider "aws" {
    region     = var.AWS_REGION
    access_key = var.ACCESS_KEY
    secret_key = var.SECRET_ACCESS_KEY 
}

resource "aws_iam_role" "provision_lambda_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version   = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
        Effect = "Allow"
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "lambda_policy" {
  role       = aws_iam_role.provision_lambda_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

resource "aws_lambda_function" "provision_lambda" {
  function_name = "c11-hermes-provision"
  role          = aws_iam_role.provision_lambda_role.arn
  package_type  = "Image"
  image_uri     = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-hermes-provision:latest"
  architectures = ["x86_64"]
  timeout       = 30

  logging_config {
    log_format        = "Text"
    log_group         = "/aws/lambda/c11-hermes-clean_lambda"
    }

  environment {
    variables = {
      DB_HOST             = var.DB_HOST
      DB_PORT             = var.DB_PORT
      DB_PASSWORD         = var.DB_PASSWORD
      DB_USER             = var.DB_USER
      DB_NAME             = var.DB_NAME
      DB_SCHEMA           = var.DB_SCHEMA
      PROCESSING_BATCH_SIZE = var.PROCESSING_BATCH_SIZE
    }
  }
}