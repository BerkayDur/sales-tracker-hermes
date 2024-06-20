# This file assigns variables to the values stored in terraform.tfvars

variable "AWS_REGION" {
  type = string
  default = "eu-west-2"
}

variable "DB_HOST" {
  type = string
}

variable "DB_NAME" {
  type = string
}

variable "DB_PASSWORD" {
  type = string
}

variable "DB_PORT" {
  type = number
}

variable "DB_USER" {
  type = string
}