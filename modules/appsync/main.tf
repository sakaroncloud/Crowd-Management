resource "aws_appsync_graphql_api" "crowdsync" {
  name                = "${var.project_name}-api-${var.environment}"
  authentication_type = "AMAZON_COGNITO_USER_POOLS"

  user_pool_config {
    aws_region     = var.aws_region
    default_action = "ALLOW"
    user_pool_id   = var.user_pool_id
  }

  additional_authentication_provider {
    authentication_type = "AWS_IAM"
  }

  log_config {
    cloudwatch_logs_role_arn = var.appsync_logs_role_arn
    field_log_level          = "ALL"
  }

  tags = {
    Environment = var.environment
    Project     = var.project_name
  }

  schema = file("${path.module}/schema.graphql")
}

resource "aws_appsync_datasource" "none" {
  api_id = aws_appsync_graphql_api.crowdsync.id
  name   = "None"
  type   = "NONE"
}

resource "aws_appsync_resolver" "update_zone_resolver" {
  api_id      = aws_appsync_graphql_api.crowdsync.id
  field       = "updateZone"
  type        = "Mutation"
  data_source = aws_appsync_datasource.none.name

  request_template = <<EOF
{
    "version": "2018-05-29",
    "payload": $util.toJson($context.arguments)
}
EOF

  response_template = <<EOF
$util.toJson($context.result)
EOF
}

# Lambda Data Source for Read operations
resource "aws_iam_role" "appsync_lambda_role" {
  name = "${var.project_name}-appsync-lambda-role-${var.environment}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "appsync.amazonaws.com"
        }
      },
    ]
  })
}

resource "aws_iam_role_policy" "appsync_lambda_policy" {
  name = "${var.project_name}-appsync-lambda-policy-${var.environment}"
  role = aws_iam_role.appsync_lambda_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = "lambda:InvokeFunction"
        Effect   = "Allow"
        Resource = var.read_handler_arn
      },
    ]
  })
}

resource "aws_appsync_datasource" "lambda_read" {
  api_id           = aws_appsync_graphql_api.crowdsync.id
  name             = "LambdaRead"
  type             = "AWS_LAMBDA"
  service_role_arn = aws_iam_role.appsync_lambda_role.arn

  lambda_config {
    function_arn = var.read_handler_arn
  }
}

# Query Resolvers
resource "aws_appsync_resolver" "list_zones" {
  api_id      = aws_appsync_graphql_api.crowdsync.id
  field       = "listZones"
  type        = "Query"
  data_source = aws_appsync_datasource.lambda_read.name

  request_template = <<EOF
{
    "version": "2018-05-29",
    "operation": "Invoke",
    "payload": $util.toJson($context)
}
EOF

  response_template = <<EOF
$util.toJson($context.result)
EOF
}

resource "aws_appsync_resolver" "get_zone" {
  api_id      = aws_appsync_graphql_api.crowdsync.id
  field       = "getZone"
  type        = "Query"
  data_source = aws_appsync_datasource.lambda_read.name

  request_template = <<EOF
{
    "version": "2018-05-29",
    "operation": "Invoke",
    "payload": $util.toJson($context)
}
EOF

  response_template = <<EOF
$util.toJson($context.result)
EOF
}

