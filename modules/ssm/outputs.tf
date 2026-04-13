output "parameter_name" {
  description = "The name of the SSM parameter"
  value       = aws_ssm_parameter.ingest_token.name
}

output "parameter_arn" {
  description = "The ARN of the SSM parameter"
  value       = aws_ssm_parameter.ingest_token.arn
}

output "ingest_token_value" {
  description = "The raw value of the ingest token (sensitive)"
  value       = random_password.ingest_token.result
  sensitive   = true
}
