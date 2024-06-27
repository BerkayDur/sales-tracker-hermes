resource "aws_security_group" "c11_hermes_dashboard_sg" {
    name        = "${var.dashboard_name}_sg"
    vpc_id = var.AWS_VPC
    description = "Allows access to streamlit dashboard"
    egress = [
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
    ingress = [
        {
            cidr_blocks      = ["0.0.0.0/0"]
            description      = ""
            from_port        = var.PORT_TO_EXPOSE
            ipv6_cidr_blocks = []
            prefix_list_ids  = []
            protocol         = "tcp"
            security_groups  = []
            self             = false
            to_port          = var.PORT_TO_EXPOSE
        },
    ]
}



resource "aws_ecs_task_definition" "dashboard_task_def" {
    family = "${var.DASHBOARD_NAME}_task_def"
    requires_compatibilities = ["FARGATE"]
    network_mode = "awsvpc"
    cpu = 1024
    memory = 3072
    execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
    container_definitions = jsonencode(([
        {
            name = var.DASHBOARD_NAME
            image = "129033205317.dkr.ecr.eu-west-2.amazonaws.com/c11-hermes-dashboard:latest"
            cpu = 1024
            memory = 3072
            essential = true
            portMappings = [
                {
                    hostPort = var.PORT_TO_EXPOSE
                    containerPort = var.PORT_TO_EXPOSE
                }
            ]
            
            environment = [
                {
                    "name" : "ACCESS_KEY",
                    "value" : var.ACCESS_KEY
                },
                {
                    "name" : "SECRET_ACCESS_KEY",
                    "value" : var.SECRET_ACCESS_KEY
                },
                {
                    "name" : "DB_HOST",
                    "value" : var.DB_HOST
                },
                {
                    "name" : "DB_PORT",
                    "value" : var.DB_PORT
                },
                {
                    "name" : "DB_PASSWORD",
                    "value" : var.DB_PASSWORD
                },
                {
                    "name" : "DB_USER",
                    "value" : var.DB_USER
                },
                {
                    "name" : "DB_NAME",
                    "value" : var.DB_NAME
                }
            ]
        }
    ]))
    runtime_platform {
      operating_system_family = "LINUX"
      cpu_architecture = "X86_64"
    }

}



resource "aws_ecs_service" "dashboard_service" {
    name = "${var.DASHBOARD_NAME}_service"
    cluster = var.CLUSTER_ARN
    task_definition = aws_ecs_task_definition.dashboard_task_def.arn
    desired_count = 1
    launch_type = "FARGATE"
    network_configuration {
      subnets = var.SUBNETS
      security_groups = [aws_security_group.c11_hermes_dashboard_sg.id]
      assign_public_ip = true
    }
}



data "aws_iam_role" "ecs_task_execution_role" {
  name = "ecsTaskExecutionRole"
}