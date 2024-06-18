# This file assigns variables to the values stored in terraform.tfvars

variable "AWS_REGION" {
  type = string
  default = "eu-west-2"
}

variable "DB_PASSWORD" {
  type = string
}