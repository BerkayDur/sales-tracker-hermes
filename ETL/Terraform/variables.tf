# This file assigns variables to the values stored in terraform.tfvars

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
