provider "aws" {
    region     = var.AWS_REGION
    access_key = var.ACCESS_KEY
    secret_key = var.SECRET_ACCESS_KEY 
}

variable "email_load_lambda_name" {
  default = "c11-hermes-email_load_lambda"
}

data "aws_iam_policy_document" "assume_role" {
    statement {
      effect = "Allow"

      principals {
        type = "Service"
        identifiers = ["lambda.amazonaws.com"]
      }
    }
}