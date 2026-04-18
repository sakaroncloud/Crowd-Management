output "queue_url" {
  value       = aws_sqs_queue.telemetry_queue.id
  description = "URL of the SQS teleport queue"
}

output "queue_arn" {
  value       = aws_sqs_queue.telemetry_queue.arn
  description = "ARN of the SQS telemetry queue"
}

output "dlq_arn" {
  value       = aws_sqs_queue.telemetry_dlq.arn
  description = "ARN of the Dead Letter Queue"
}

output "dlq_name" {
  value = aws_sqs_queue.telemetry_dlq.name
}

output "queue_name" {
  value = aws_sqs_queue.telemetry_queue.name
}
