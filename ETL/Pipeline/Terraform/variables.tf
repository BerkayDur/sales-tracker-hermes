variable "extract_price_readings_lambda_name" {
  default = "c11-hermes-extract_price_readings-lambda"
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
