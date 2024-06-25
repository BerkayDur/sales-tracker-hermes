
resource "aws_ecs_task_definition" "dashboard_task_def" {
    family = var.dashboard_name
    requires_compatibilities = ["FARGATE"]
    network_mode = "awsvpc"
    cpu = 1024
    memory = 3072
    execution_role_arn = data.aws_iam_role.ecs_task_execution_role.arn
    container_definitions = jsonencode(([
        {
            name = "c11-berkay-better-cheese-truck-dashboard-terraform-test"
            # image = Fill this in later
            cpu = 1024
            memory = 3072
            essential = true
            portMappings = [
                {
                    hostPort = 80
                    containerPort = 80
                },
                {
                    hostPort = 8501
                    containerPort = 8501
                }
            ]
            environment = [
                {
                    "name": "DB_HOST",
                    "value": var.DB_HOST
                },
                {
                    "name": "DB_NAME",
                    "value": var.DB_NAME
                },
                {
                    "name": "DB_PASSWORD",
                    "value": var.DB_PASSWORD
                },
                {
                    "name": "DB_PORT",
                    "value": var.DB_PORT
                },
                {
                    "name": "DB_USER",
                    "value": var.DB_USER
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
    name = "c11-berkay-terraform-dashboard-service"
    cluster = var.cluster_arn
    task_definition = aws_ecs_task_definition.dashboard_task_def.arn
    desired_count = 1
    launch_type = "FARGATE"
    network_configuration {
      subnets = ["subnet-04ec64625db90bc59", "subnet-0680e82f872693b78", "subnet-0af173a8d980c9354"]
      security_groups = ["sg-02e2c7112e97629d3"]
      assign_public_ip = true
    }
}
