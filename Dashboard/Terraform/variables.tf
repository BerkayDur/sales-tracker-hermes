variable "dashboard_name" {
  default = "c11-hermes-dashboard-tf-1"
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

variable "CLUSTER_ARN" {
    type = string
}

variable "SUBNETS" {
    type=list(string)
}

variable "AWS_VPC" {
    type = string
}

variable "DASHBAORD_SG" {
    type = string
}

variable "PORT_TO_EXPOSE" {
    type = string
    default = "8501"
}