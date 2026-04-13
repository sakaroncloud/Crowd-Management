output "ingest_lambda_arn" {
  description = "The ARN of the Ingest Lambda function"
  value       = aws_lambda_function.ingest.arn
}

output "read_lambda_arn" {
  description = "The ARN of the Read Lambda function"
  value       = aws_lambda_function.read.arn
}

output "ingest_lambda_name" {
  description = "The name of the Ingest Lambda function"
  value       = aws_lambda_function.ingest.function_name
}

output "read_lambda_name" {
  description = "The name of the Read Lambda function"
  value       = aws_lambda_function.read.function_name
}

output "read_lambda_invoke_arn" {
  description = "The invoke ARN of the Read Lambda function"
  value       = aws_lambda_function.read.invoke_arn
}

output "ingest_lambda_invoke_arn" {
  description = "The invoke ARN of the Ingest Lambda function"
  value       = aws_lambda_function.ingest.invoke_arn
}

output "auth_lambda_arn" {
  description = "The ARN of the Authorizer Lambda function"
  value       = aws_lambda_function.authorizer.arn
}

output "auth_lambda_invoke_arn" {
  description = "The invoke ARN of the Authorizer Lambda function"
  value       = aws_lambda_function.authorizer.invoke_arn
}

