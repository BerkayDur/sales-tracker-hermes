# This file outputs information about the lambda function

output "state_machine_name" {
  value = aws_sfn_state_machine.etl_state_machine.name
}

output "scheduler_name" {
  value = aws_scheduler_schedule.etl_pipeline_state_machine_schedule.name
}