# This file assigns variables to the values stored in terraform.tfvars


variable "clean_up_name" {
  type = string
  default = "c11-hermes-clean-up-tf-2"
}

variable "AWS_REGION" {
  type = string
  default = "eu-west-2"
}

variable "ACCESS_KEY" {
  type = string
}

variable "SECRET_ACCESS_KEY" {
  type = string
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