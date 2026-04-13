resource "aws_apigatewayv2_api" "http" {
  name          = "${var.project_name}-api-${var.environment}"
  protocol_type = "HTTP"

  cors_configuration {
    allow_origins = ["*"]
    allow_methods = ["POST", "GET", "OPTIONS"]
    allow_headers = ["content-type", "authorization"]
    max_age       = 300
  }

  tags = {
    Name = "${var.project_name}-api"
  }
}

resource "aws_apigatewayv2_stage" "default" {
  api_id      = aws_apigatewayv2_api.http.id
  name        = "$default"
  auto_deploy = true

  access_log_settings {
    destination_arn = aws_cloudwatch_log_group.api_logs.arn
    format          = jsonencode({
      requestId      = "$context.requestId"
      ip             = "$context.identity.sourceIp"
      requestTime    = "$context.requestTime"
      httpMethod     = "$context.httpMethod"
      routeKey       = "$context.routeKey"
      status         = "$context.status"
      protocol       = "$context.protocol"
      responseLength = "$context.responseLength"
    })
  }
}

resource "aws_cloudwatch_log_group" "api_logs" {
  name              = "/aws/apigateway/${var.project_name}-api-${var.environment}"
  retention_in_days = 7
}

# Integrations
resource "aws_apigatewayv2_integration" "ingest" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = var.ingest_lambda_invoke_arn
  payload_format_version = "2.0"
}

resource "aws_apigatewayv2_integration" "read" {
  api_id                 = aws_apigatewayv2_api.http.id
  integration_type       = "AWS_PROXY"
  integration_uri        = var.read_lambda_invoke_arn
  payload_format_version = "2.0"
}

# Authorizers
resource "aws_apigatewayv2_authorizer" "cognito" {
  api_id           = aws_apigatewayv2_api.http.id
  authorizer_type  = "JWT"
  identity_sources = ["$request.header.Authorization"]
  name             = "cognito-authorizer"

  jwt_configuration {
    audience = [var.user_pool_client_id]
    issuer   = "https://cognito-idp.${data.aws_region.current.name}.amazonaws.com/${var.user_pool_id}"
  }
}

resource "aws_apigatewayv2_authorizer" "lambda" {
  api_id                            = aws_apigatewayv2_api.http.id
  authorizer_type                   = "REQUEST"
  authorizer_uri                    = var.auth_lambda_invoke_arn
  identity_sources                  = ["$request.header.x-api-token"]
  name                              = "token-authorizer"
  authorizer_payload_format_version = "2.0"
  enable_simple_responses           = true
}

data "aws_region" "current" {}

# Routes
resource "aws_apigatewayv2_route" "post_data" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "POST /crowd-data"
  target             = "integrations/${aws_apigatewayv2_integration.ingest.id}"
  authorization_type = "CUSTOM"
  authorizer_id      = aws_apigatewayv2_authorizer.lambda.id
}


resource "aws_apigatewayv2_route" "get_zones" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "GET /zones"
  target             = "integrations/${aws_apigatewayv2_integration.read.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}

resource "aws_apigatewayv2_route" "get_zone_by_id" {
  api_id             = aws_apigatewayv2_api.http.id
  route_key          = "GET /zones/{id}"
  target             = "integrations/${aws_apigatewayv2_integration.read.id}"
  authorization_type = "JWT"
  authorizer_id      = aws_apigatewayv2_authorizer.cognito.id
}


# Permissions for Lambda
resource "aws_lambda_permission" "api_ingest" {
  statement_id  = "AllowAPIGatewayInvokeIngest"
  action        = "lambda:InvokeFunction"
  function_name = var.ingest_lambda_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_read" {
  statement_id  = "AllowAPIGatewayInvokeRead"
  action        = "lambda:InvokeFunction"
  function_name = var.read_lambda_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_auth" {
  statement_id  = "AllowAPIGatewayInvokeAuth"
  action        = "lambda:InvokeFunction"
  function_name = var.auth_lambda_arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_apigatewayv2_api.http.execution_arn}/*/*"
}

