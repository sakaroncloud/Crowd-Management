output "api_endpoint" {
  description = "The endpoint URL of the API Gateway"
  value       = module.api_gateway.api_endpoint
}

output "cognito_user_pool_id" {
  description = "The ID of the Cognito User Pool"
  value       = module.cognito.user_pool_id
}

output "cognito_client_id" {
  description = "The ID of the Cognito User Pool Client"
  value       = module.cognito.user_pool_client_id
}

output "ingest_token" {
  description = "The API token for the crowd data ingest endpoint"
  value       = module.ssm.ingest_token_value
  sensitive   = true
}

output "frontend_url" {
  description = "The CloudFront URL of the hosted React frontend"
  value       = module.frontend.cloudfront_url
}
