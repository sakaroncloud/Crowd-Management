# CloudWatch Alarms for Monitoring

# 1. Lambda Errors - Ingestion
resource "aws_cloudwatch_metric_alarm" "ingest_lambda_errors" {
  alarm_name          = "${var.project_name}-ingest-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This alarm triggers when the Ingestion Lambda fails."
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]

  dimensions = {
    FunctionName = var.ingest_lambda_name
  }

  tags = var.tags
}

# 2. Lambda Errors - Read
resource "aws_cloudwatch_metric_alarm" "read_lambda_errors" {
  alarm_name          = "${var.project_name}-read-errors-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "Errors"
  namespace           = "AWS/Lambda"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This alarm triggers when the Read Lambda fails."
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]

  dimensions = {
    FunctionName = var.read_lambda_name
  }

  tags = var.tags
}

# 3. API Gateway 5XX Errors
resource "aws_cloudwatch_metric_alarm" "api_5xx_errors" {
  alarm_name          = "${var.project_name}-api-5xx-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "5XXError"
  namespace           = "AWS/ApiGateway"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This alarm triggers when the API Gateway returns 5XX responses."
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]

  dimensions = {
    ApiId = var.api_id
    Stage = "$default"
  }

  tags = var.tags
}

# 4. SQS Backlog Alarm
resource "aws_cloudwatch_metric_alarm" "sqs_backlog" {
  alarm_name          = "${var.project_name}-sqs-backlog-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name         = "ApproximateNumberOfMessagesVisible"
  namespace           = "AWS/SQS"
  period              = "60"
  statistic           = "Average"
  threshold           = "1000" # Alert if more than 1000 messages are waiting
  alarm_description   = "This alarm triggers when the teleport queue has a high backlog."
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]

  dimensions = {
    QueueName = var.queue_name
  }

  tags = var.tags
}

# 5. SQS DLQ Messages Alarm
resource "aws_cloudwatch_metric_alarm" "sqs_dlq" {
  alarm_name          = "${var.project_name}-sqs-dlq-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "NumberOfMessagesReceived"
  namespace           = "AWS/SQS"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0" # Alert if any message hits the DLQ
  alarm_description   = "This alarm triggers when a message fails processing and enters the DLQ."
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]

  dimensions = {
    QueueName = var.dlq_name
  }

  tags = var.tags
}

# 6. DynamoDB Write Throttling Alarm
resource "aws_cloudwatch_metric_alarm" "dynamodb_throttling" {
  alarm_name          = "${var.project_name}-dynamodb-throttling-${var.environment}"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "1"
  metric_name         = "WriteThrottleEvents"
  namespace           = "AWS/DynamoDB"
  period              = "60"
  statistic           = "Sum"
  threshold           = "0"
  alarm_description   = "This alarm triggers when DynamoDB write requests are throttled."
  alarm_actions       = [var.sns_topic_arn]
  ok_actions          = [var.sns_topic_arn]

  dimensions = {
    TableName = var.dynamodb_table_name
  }

  tags = var.tags
}
