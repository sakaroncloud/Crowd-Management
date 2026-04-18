resource "aws_sqs_queue" "telemetry_dlq" {
  name                      = "${var.project_name}-telemetry-dlq-${var.environment}"
  message_retention_seconds = 1209600 # 14 days
  tags                      = var.tags
}

resource "aws_sqs_queue" "telemetry_queue" {
  name                      = "${var.project_name}-telemetry-queue-${var.environment}"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 86400 # 1 day, since crowd data is real-time
  receive_wait_time_seconds = 10    # Long polling

  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.telemetry_dlq.arn
    maxReceiveCount     = 3
  })

  tags = var.tags
}
