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
    Stage = "$$default"
  }

  tags = var.tags
}
