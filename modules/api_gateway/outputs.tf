output "api_endpoint" {
  description = "The endpoint URL of the API Gateway"
  value       = aws_apigatewayv2_api.http.api_endpoint
}

output "api_id" {
  description = "The ID of the API Gateway"
  value       = aws_apigatewayv2_api.http.id
}

