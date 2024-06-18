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
    db_name                               = "sales"
    availability_zone                     = "eu-west-2a"
    copy_tags_to_snapshot                 = true
    db_subnet_group_name                  = "c11-public-subnet-group"
    engine                                = "postgres"
    engine_version                        = "16.3"
    identifier                            = "c11-hermes-db"
    instance_class                        = "db.t3.micro"
    license_model                         = "postgresql-license"
    network_type                          = "IPV4"
    port                                  = 5432
    password                              = var.DB_PASSWORD
    publicly_accessible                   = true
    skip_final_snapshot                   = true
    storage_encrypted                     = true
    username                              = "postgres"
    vpc_security_group_ids                = ["sg-0599fe57129262ed0"]
}