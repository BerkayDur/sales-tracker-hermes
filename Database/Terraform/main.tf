# This file terraforms the database on AWS RDS

terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.AWS_REGION
}

# terraform import aws_db_instance.database c11-hermes-db
resource "aws_db_instance" "database" {
    allocated_storage                     = 20
    db_name                               = var.DB_NAME
    availability_zone                     = var.AWS_AZ
    copy_tags_to_snapshot                 = true
    db_subnet_group_name                  = var.DB_SUBNET
    engine                                = "postgres"
    engine_version                        = "16.3"
    identifier                            = var.RDS_NAME
    instance_class                        = "db.t3.micro"
    license_model                         = "postgresql-license"
    network_type                          = "IPV4"
    port                                  = var.DB_PORT
    password                              = var.DB_PASSWORD
    publicly_accessible                   = true
    skip_final_snapshot                   = true
    storage_encrypted                     = true
    username                              = var.DB_USERNAME
    vpc_security_group_ids                = [aws_security_group.c11_hermes_sg.id]
}

# terraform import aws_security_group.c11_hermes_sg sg-0599fe57129262ed0
resource "aws_security_group" "c11_hermes_sg" {
    name        = var.SG_NAME
    vpc_id = var.AWS_VPC
    description = "Allows access to port ${var.DB_PORT}"
    egress      = [
        {
            cidr_blocks      = ["0.0.0.0/0"]
            description      = ""
            from_port        = 0
            ipv6_cidr_blocks = []
            prefix_list_ids  = []
            protocol         = "-1"
            security_groups  = []
            self             = false
            to_port          = 0
        },
    ]
    ingress     = [
        {
            cidr_blocks      = ["0.0.0.0/0"]
            description      = ""
            from_port        = var.DB_PORT
            ipv6_cidr_blocks = []
            prefix_list_ids  = []
            protocol         = "tcp"
            security_groups  = []
            self             = false
            to_port          = var.DB_PORT
        },
    ]
}