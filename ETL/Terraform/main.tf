# This file terraforms the Step Function and EventBridge Scheduler for the ETL pipeline

provider "aws" {
    region     = var.AWS_REGION
    access_key = var.ACCESS_KEY
    secret_key = var.SECRET_ACCESS_KEY 
}

# ETL State Machine

resource "aws_sfn_state_machine" "etl_state_machine" {
  name     = "c11-hermes-sale-tracker-state-machine"
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
          FunctionName = "arn:aws:lambda:eu-west-2:129033205317:function:c11-hermes-provision:$LATEST"
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
                FunctionName = "arn:aws:lambda:eu-west-2:129033205317:function:c11-hermes-extract_price_readings-lambda:$LATEST"
              },
              End = true,
              OutputPath: "$.Payload"
            }
          }
        },
        Next = "Aggregate Data",
        Label = "GetProductDatainParallel",
        MaxConcurrency = 5,
        InputPath = "$.output"
      },
      "Aggregate Data" = {
        Type     = "Task",
        Resource = "arn:aws:states:::lambda:invoke",
        OutputPath = "$.Payload",
        Parameters = {
          "Payload.$"    = "$",
          FunctionName = "arn:aws:lambda:eu-west-2:129033205317:function:c11-hermes-email-load-lambda:$LATEST"
        },
        End = true
      }
    }
  })
}

resource "aws_iam_role" "sfn_role" {
  name = "sfn_role"

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
          "arn:aws:lambda:eu-west-2:129033205317:function:c11-hermes-provision:$LATEST",
          "arn:aws:lambda:eu-west-2:129033205317:function:c11-hermes-extract_price_readings-lambda:$LATEST",
          "arn:aws:lambda:eu-west-2:129033205317:function:c11-hermes-email-load-lambda:$LATEST",
          "arn:aws:states:eu-west-2:129033205317:stateMachine:c11-hermes-etl-state-machine"
        ]
      }
    ]
  })
}

# ETL Scheduler

resource "aws_iam_role" "scheduler_role" {
  name = "scheduler_role"

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
        Resource = "arn:aws:states:eu-west-2:129033205317:stateMachine:c11-hermes-sale-tracker-state-machine"
      }
    ]
  })
}

resource "aws_scheduler_schedule" "etl_pipeline_state_machine_schedule" {
    name = "c11-hermes-etl-schedule"
    flexible_time_window {
      mode = "OFF"
    }
    schedule_expression = "cron(*/3 * * * ? *)"
    target {
        arn=aws_sfn_state_machine.etl_state_machine.arn
        role_arn = aws_iam_role.scheduler_role.arn
    }
}