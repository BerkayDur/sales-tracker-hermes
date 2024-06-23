# This file assigns variables to the values stored in terraform.tfvars

variable "max_concurrency" {
  type = number
  default = 5
}

variable "email_load_lambda_name" {
  default = "c11-hermes-email-load-lambda-2"
}

variable "provision_lambda_name" {
    default = "c11-hermes-provisioning-lambda-2"
}

variable "etl_lambda_name" {
    default = "c11-hermes-etl-lambda-2"
}

variable "etl_step_function_name" {
    default = "c11-hermes-sale-tracker-state-machine-2"
}

variable "ACCESS_KEY" {
    type = string
}

variable "SECRET_ACCESS_KEY" {
    type = string
}

variable "AWS_REGION" {
    type = string
    default = "eu-west-2" 
}

variable "DB_HOST" {
    type = string
}

variable "DB_PORT" {
    type = number
    default = 1433
}

variable "DB_PASSWORD" {
    type = string
}

variable "DB_USER" {
    type = string
}

variable "DB_NAME" {
    type = string
}

variable "DB_SCHEMA" {
    type = string
}

variable "PROCESSING_BATCH_SIZE" {
    type = number
}