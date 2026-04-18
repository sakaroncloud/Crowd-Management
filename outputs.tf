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
output "graphql_endpoint" {
  description = "The URL of the AppSync GraphQL endpoint"
  value       = module.appsync.graphql_api_url
}

output "distribution_id" {
  description = "The ID of the CloudFront distribution"
  value       = module.frontend.cloudfront_id
}
