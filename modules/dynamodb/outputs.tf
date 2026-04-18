output "table_name" {
  description = "The name of the DynamoDB table"
  value       = aws_dynamodb_table.crowd_zones.name
}

output "table_arn" {
  description = "The ARN of the DynamoDB table"
  value       = aws_dynamodb_table.crowd_zones.arn
}
output "stream_arn" {
  description = "The ARN of the DynamoDB table stream"
  value       = aws_dynamodb_table.crowd_zones.stream_arn
}
output "metadata_table_name" {
  description = "The name of the DynamoDB metadata table"
  value       = aws_dynamodb_table.crowd_metadata.name
}

output "metadata_table_arn" {
  description = "The ARN of the DynamoDB metadata table"
  value       = aws_dynamodb_table.crowd_metadata.arn
}
