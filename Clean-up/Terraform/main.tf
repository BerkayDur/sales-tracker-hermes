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
}

# terraform import aws_lambda_function.c11-hermes-clean_lambda c11-hermes-clean_lambda
resource "aws_lambda_function" "c11-hermes-clean_lambda" {
    function_name                  = "c11-hermes-clean_lambda"
    image_uri                      = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-hermes-clean@sha256:e9ccc95322d51a339b97f61fc1f109b1f9f0d21a4598c3d470c6f857328587ca"
    package_type                   = "Image"
    role                           = "arn:aws:iam::129033205317:role/service-role/c11-hermes-clean_lambda-role-yk4tvt6d"

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
        log_group         = "/aws/lambda/c11-hermes-clean_lambda"
    }

    tracing_config {
        mode = "PassThrough"
    }
}

# terraform import aws_cloudwatch_event_rule.c11-hermes-clean-daily default/c11-hermes-clean-daily
resource "aws_cloudwatch_event_rule" "c11-hermes-clean-daily" {
    description         = "Runs every day"
    name                = "c11-hermes-clean-daily"
    schedule_expression = "cron(0 0 * * ? *)"
}

# terraform import aws_cloudwatch_event_target.c11-hermes-clean-daily-target default/c11-hermes-clean-daily/6lshg4d2i72jbq4o4mj2u
resource "aws_cloudwatch_event_target" "c11-hermes-clean-daily-target" {
    depends_on = [ aws_cloudwatch_event_rule.c11-hermes-clean-daily, aws_lambda_function.c11-hermes-clean_lambda ]
    arn            = "arn:aws:lambda:eu-west-2:129033205317:function:c11-hermes-clean_lambda"
    rule           = "c11-hermes-clean-daily"
}