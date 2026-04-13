output "user_pool_id" {
  description = "The ID of the Cognito User Pool"
  value       = aws_cognito_user_pool.pool.id
}

output "user_pool_arn" {
  description = "The ARN of the Cognito User Pool"
  value       = aws_cognito_user_pool.pool.arn
}

output "user_pool_client_id" {
  description = "The ID of the Cognito User Pool Client"
  value       = aws_cognito_user_pool_client.client.id
}

output "user_pool_domain" {
  description = "The domain of the Cognito User Pool"
  value       = aws_cognito_user_pool_domain.main.domain
}
