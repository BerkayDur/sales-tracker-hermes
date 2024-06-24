# This file terraforms the Step Function and EventBridge Scheduler for the ETL pipeline

provider "aws" {
    region     = var.AWS_REGION
    access_key = var.ACCESS_KEY
    secret_key = var.SECRET_ACCESS_KEY 
}

# Shared utility

data "aws_iam_policy_document" "lambda_assume_doc" {
    statement {
      effect = "Allow"

      principals {
        type = "Service"
        identifiers = ["lambda.amazonaws.com"]
      }

      actions = ["sts:AssumeRole"]
    }
}

data "aws_iam_policy_document" "lambda_logging_doc" {
    statement {
        effect = "Allow"
        actions = [
            "logs:CreateLogGroup",
            "logs:CreateLogStream",
            "logs:PutLogEvents"
        ]

        resources = ["arn:aws:logs:*:*:*"]
    }
}


# Provisioning Lambda

resource "aws_iam_role" "iam_for_provisioning_lambda" {
  name = "c11-hermes-provisioning-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_doc.json
}

resource "aws_cloudwatch_log_group" "provisioning_lambda_cloudwatch" {
  name              = "/aws/lambda/${var.provision_lambda_name}"
  retention_in_days = 14
}


resource "aws_iam_policy" "provisioning_lambda_logging" {
    name = "c11-hermes-provisioning-lambda-logging"
    path = "/"
    description = "IAM policy for logging from a lambda."
    policy = data.aws_iam_policy_document.lambda_logging_doc.json
}

resource "aws_iam_role_policy_attachment" "provisioning_lambda_logging" {
  role = aws_iam_role.iam_for_provisioning_lambda.name
  policy_arn = aws_iam_policy.provisioning_lambda_logging.arn
}

resource "aws_lambda_function" "provisioning_lambda" {
    function_name = var.provision_lambda_name
    role = aws_iam_role.iam_for_provisioning_lambda.arn
    image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-hermes-provision:latest"
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
    package_type = "Image"
    depends_on = [
    aws_iam_role_policy_attachment.provisioning_lambda_logging,
    aws_cloudwatch_log_group.provisioning_lambda_cloudwatch
    ]
    memory_size = 3008
    timeout = 60
}

# ETL Lambda


resource "aws_iam_role" "iam_for_etl_lambda" {
  name = "c11-hermes-etl-lambda-role"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_doc.json
}

resource "aws_cloudwatch_log_group" "etl_lambda_cloudwatch" {
  name              = "/aws/lambda/${var.etl_lambda_name}"
  retention_in_days = 14
}


resource "aws_iam_policy" "etl_lambda_logging" {
    name = "c11-hermes-etl-lambda-logging"
    path = "/"
    description = "IAM policy for logging from a lambda."
    policy = data.aws_iam_policy_document.lambda_logging_doc.json
}

resource "aws_iam_role_policy_attachment" "etl_lambda_logging" {
  role = aws_iam_role.iam_for_etl_lambda.name
  policy_arn = aws_iam_policy.etl_lambda_logging.arn
}

resource "aws_lambda_function" "etl_lambda" {
    function_name = var.etl_lambda_name
    role = aws_iam_role.iam_for_etl_lambda.arn
    image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-hermes-extract-readings:latest"
    environment {
        variables = {
            ACCESS_KEY = var.ACCESS_KEY,
            SECRET_ACCESS_KEY = var.SECRET_ACCESS_KEY
        }
    }
    package_type = "Image"
    depends_on = [
    aws_iam_role_policy_attachment.etl_lambda_logging,
    aws_cloudwatch_log_group.etl_lambda_cloudwatch
    ]
    memory_size = 3008
    timeout = 60
}

# Email Lambda

resource "aws_iam_role" "iam_for_email_load_lambda" {
  name = "c11-hermes-email-load-lambda-role-2"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume_doc.json
}

resource "aws_cloudwatch_log_group" "email_load_lambda_cloudwatch" {
  name              = "/aws/lambda/${var.email_load_lambda_name}-2"
  retention_in_days = 14
}


resource "aws_iam_policy" "email_load_lambda_logging" {
    name = "c11-hermes-email-load-lambda-logging-2"
    path = "/"
    description = "IAM policy for logging from a lambda."
    policy = data.aws_iam_policy_document.lambda_logging_doc.json
}

resource "aws_iam_role_policy_attachment" "email_load_lambda_logging" {
  role = aws_iam_role.iam_for_email_load_lambda.name
  policy_arn = aws_iam_policy.email_load_lambda_logging.arn
}

resource "aws_lambda_function" "email_load_lambda" {
    function_name = var.email_load_lambda_name
    role = aws_iam_role.iam_for_email_load_lambda.arn
    image_uri = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-hermes-email-load-lambda-registry:latest"
    environment {
        variables = {
            DB_HOST = var.DB_HOST,
            DB_PORT = var.DB_PORT,
            DB_NAME = var.DB_NAME,
            DB_USER = var.DB_USER,
            DB_PASSWORD = var.DB_PASSWORD,
            ACCESS_KEY = var.ACCESS_KEY,
            SECRET_ACCESS_KEY = var.SECRET_ACCESS_KEY
        }
    }
    package_type = "Image"
    depends_on = [
    aws_iam_role_policy_attachment.email_load_lambda_logging,
    aws_cloudwatch_log_group.email_load_lambda_cloudwatch
    ]
    memory_size = 3008
    timeout = 60
}

# ETL State Machine

resource "aws_sfn_state_machine" "etl_state_machine" {
  name     = var.etl_step_function_name
  role_arn = aws_iam_role.sfn_role.arn

  definition = jsonencode({
    Comment = "The state machine for hermes sale tracker ETL pipeline",
    StartAt = "Provision",
    States = {
      Provision = {
        Type     = "Task",
        Resource = "arn:aws:states:::lambda:invoke",
        OutputPath = "$.Payload",
        Parameters = {
          "Payload.$"    = "$",
          FunctionName = aws_lambda_function.provisioning_lambda.arn
        },
        Next = "Get Product Data in Parallel",
        OutputPath: "$.Payload"
      },
      "Get Product Data in Parallel" = {
        Type = "Map",
        ItemProcessor = {
          ProcessorConfig = {
            Mode          = "INLINE"
          },
          StartAt = "Scrape Product Data",
          States = {
            "Scrape Product Data" = {
              Type     = "Task",
              Resource = "arn:aws:states:::lambda:invoke",
              OutputPath = "$.Payload",
              Parameters = {
                "Payload.$"    = "$",
                FunctionName = aws_lambda_function.etl_lambda.arn
              },
              End = true,
              OutputPath: "$.Payload"
            }
          }
        },
        Next = "Aggregate Data",
        Label = "GetProductDatainParallel",
        MaxConcurrency = var.max_concurrency,
        InputPath = "$.output"
      },
      "Aggregate Data" = {
        Type     = "Task",
        Resource = "arn:aws:states:::lambda:invoke",
        OutputPath = "$.Payload",
        Parameters = {
          "Payload.$"    = "$",
          FunctionName = aws_lambda_function.email_load_lambda.arn
        },
        End = true
      }
    }
  })
}

resource "aws_iam_role" "sfn_role" {
  name = "c11-step-function-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "states.eu-west-2.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "sfn_role_policy" {
  name   = "sfn_role_policy"
  role   = aws_iam_role.sfn_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect   = "Allow",
        Action   = [
          "lambda:InvokeFunction",
          "states:StartExecution"
        ],
        Resource = [
          aws_lambda_function.provisioning_lambda.arn,
          aws_lambda_function.etl_lambda.arn,
          aws_lambda_function.email_load_lambda.arn,
          aws_sfn_state_machine.etl_state_machine.arn
        ]
      }
    ]
  })
}

# ETL Scheduler

resource "aws_iam_role" "scheduler_role" {
  name = "c11_hermes_scheduler_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Principal = {
          Service = "scheduler.amazonaws.com"
        },
        Action = "sts:AssumeRole"
      }
    ]
  })
}

resource "aws_iam_role_policy" "scheduler_role_policy" {
  name   = "scheduler_role_policy"
  role   = aws_iam_role.scheduler_role.id
  policy = jsonencode({
    Version = "2012-10-17",
    Statement = [
      {
        Effect = "Allow",
        Action = [
          "states:StartExecution"
        ],
        Resource = aws_sfn_state_machine.etl_state_machine.arn
      }
    ]
  })
}

resource "aws_scheduler_schedule" "etl_pipeline_state_machine_schedule" {
    name = var.etl_scheduler_name
    flexible_time_window {
      mode = "OFF"
    }
    schedule_expression = "cron(*/3 * * * ? *)"
    target {
        arn=aws_sfn_state_machine.etl_state_machine.arn
        role_arn = aws_iam_role.scheduler_role.arn
    }
}