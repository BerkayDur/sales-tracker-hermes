# This file terraforms lambda and eventbridge on AWS

terraform {
    required_providers {
        aws = {
            source  = "hashicorp/aws"
            version = "~> 5.0"
        }
    }
}

provider "aws" {
    region = var.AWS_REGION
    access_key = var.ACCESS_KEY
    secret_key = var.SECRET_ACCESS_KEY 

}

resource "aws_lambda_function" "c11-hermes-clean_lambda" {
    function_name         = "${var.clean_up_name}_lambda"
    image_uri             = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-hermes-clean@sha256:e9ccc95322d51a339b97f61fc1f109b1f9f0d21a4598c3d470c6f857328587ca"
    package_type          = "Image"
    architectures         = ["x86_64"]
    role                  = aws_iam_role.lambda_role.arn

    environment {
        variables = {
            "DB_HOST"     = var.DB_HOST
            "DB_NAME"     = var.DB_NAME
            "DB_PASSWORD" = var.DB_PASSWORD
            "DB_PORT"     = var.DB_PORT
            "DB_USER"     = var.DB_USER
        }
    }

    logging_config {
        log_format        = "Text"
        log_group         = "/aws/lambda/${var.clean_up_name}_log_group"
    }

    tracing_config {
        mode = "PassThrough"
    }
}

resource "aws_cloudwatch_event_rule" "c11-hermes-clean-daily" {
    description         = "Runs every day at midnight"
    name                = "${var.clean_up_name}_event_rule"
    schedule_expression = "cron(0 0 * * ? *)"
}

resource "aws_cloudwatch_event_target" "c11-hermes-clean-daily-target" {
    depends_on     = [ aws_lambda_function.c11-hermes-clean_lambda ]
    arn            = aws_lambda_function.c11-hermes-clean_lambda.arn
    rule           = aws_cloudwatch_event_rule.c11-hermes-clean-daily.name
}

resource "aws_iam_role" "lambda_role" {
    assume_role_policy    = jsonencode(
        {
            Statement = [
                {
                    Action    = "sts:AssumeRole"
                    Effect    = "Allow"
                    Principal = {
                        Service = "lambda.amazonaws.com"
                    }
                },
            ]
            Version   = "2012-10-17"
        }
    )
    managed_policy_arns   = [
        "arn:aws:iam::129033205317:policy/service-role/AWSLambdaBasicExecutionRole-99772b07-38c2-414a-b7b0-c3a33f7f0b29",
    ]
    name                  = "${var.clean_up_name}-lambda-role-yk4tvt6d"
    path                  = "/service-role/"
}