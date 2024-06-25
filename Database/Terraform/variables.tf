# This file assigns variables to the values stored in terraform.tfvars

variable "AWS_REGION" {
  type = string
  default = "eu-west-2"
}

variable "DB_PASSWORD" {
  type = string
}

variable "DB_USERNAME" {
  type = string
  default = "postgres"
}

variable "DB_PORT" {
  type = number
  default = 5432
}

variable "DB_NAME" {
  type = string
  default = "sales_tracker"
}

variable "RDS_NAME" {
  type = string
  default = "c11-hermes-db-tf-1"
}

variable "DB_SUBNET" {
  type = string
  default = "c11-public-subnet-group"
}

variable "SG_NAME" {
  type = string
  default = "c11-hermes-sg-tf-1"
}

variable "AWS_AZ" {
  type = string
  default = "eu-west-2a"
}

variable "AWS_VPC" {
  type = string
}