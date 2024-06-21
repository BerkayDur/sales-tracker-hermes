provider "aws" {
    region     = var.AWS_REGION
    access_key = var.ACCESS_KEY
    secret_key = var.SECRET_ACCESS_KEY 
}

data "aws_iam_policy_document" "assume_role" {
    statement {
      effect = "Allow"

      principals {
        type = "Service"
        identifiers = ["lambda.amazonaws.com"]
      }

      actions = ["sts:AssumeRole"]
    }
}

resource "aws_iam_role" "iam_for_extract_price_readings_lambda" {
  name = "c11-hermes-extract_price_readings-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.assume_role.json
}

resource "aws_cloudwatch_log_group" "extract_price_readings_lambda_cloudwatch" {
    name = "/aws/lambda/${var.extract_price_readings_lambda_name}"
    retention_in_days = 1
}

data "aws_iam_policy_document" "extract_price_readings_lambda_logging" {
    statement {
        effect = "Allow"
        actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents",
        ]

        resources = ["arn:aws:logs:*:*:*"]
    }
}

resource "aws_iam_policy" "extract_price_readings_lambda_logging" {
    name = "c11-hermes-extract_price_readings-lambda-logging"
    path = "/"
    description = "IAM policy for logging from a lambda."
    policy = data.aws_iam_policy_document.extract_price_readings_lambda_logging.json
}

resource "aws_iam_role_policy_attachment" "extract_price_readings_lambda_logging" {
  role = aws_iam_role.iam_for_extract_price_readings_lambda.name
  policy_arn = aws_iam_policy.extract_price_readings_lambda_logging.arn
}

resource "aws_lambda_function" "extract_price_readings_test_lambda" {
    function_name = var.extract_price_readings_lambda_name
    role = aws_iam_role.iam_for_extract_price_readings_lambda.arn
    image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-hermes-extract-readings:latest"
    environment {
        variables = {
            ACCESS_KEY = "${var.ACCESS_KEY}",
            SECRET_ACCESS_KEY = "${var.SECRET_ACCESS_KEY}"
        }
    }
    package_type = "Image"
    depends_on = [
    aws_iam_role_policy_attachment.extract_price_readings_lambda_logging,
    aws_cloudwatch_log_group.extract_price_readings_lambda_cloudwatch
    ]
    memory_size = 3008
    timeout = 60
}