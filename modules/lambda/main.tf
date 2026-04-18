data "archive_file" "ingest_lambda_zip" {
  type        = "zip"
  source_file = "${path.root}/lambda_src/ingest_handler.py"
  output_path = "${path.module}/ingest_handler.zip"
}

data "archive_file" "read_lambda_zip" {
  type        = "zip"
  source_file = "${path.root}/lambda_src/read_handler.py"
  output_path = "${path.module}/read_handler.zip"
}

data "archive_file" "auth_lambda_zip" {
  type        = "zip"
  source_file = "${path.root}/lambda_src/authorizer_handler.py"
  output_path = "${path.module}/authorizer_handler.zip"
}

resource "aws_lambda_function" "ingest" {
  filename         = data.archive_file.ingest_lambda_zip.output_path
  function_name    = "${var.project_name}-ingest-${var.environment}"
  role             = var.lambda_role_arn
  handler          = "ingest_handler.lambda_handler"
  source_code_hash = data.archive_file.ingest_lambda_zip.output_base64sha256
  runtime          = "python3.9"

  environment {
    variables = {
      TABLE_NAME          = var.dynamodb_table_name
      METADATA_TABLE      = var.metadata_table_name
      BUCKET_NAME         = var.s3_bucket_name
      TOPIC_ARN           = var.sns_topic_arn
    }
  }

  tags = {
    Name = "${var.project_name}-ingest"
  }
}

resource "aws_lambda_function" "read" {
  filename         = data.archive_file.read_lambda_zip.output_path
  function_name    = "${var.project_name}-read-${var.environment}"
  role             = var.lambda_role_arn
  handler          = "read_handler.lambda_handler"
  source_code_hash = data.archive_file.read_lambda_zip.output_base64sha256
  runtime          = "python3.9"

  environment {
    variables = {
      TABLE_NAME     = var.dynamodb_table_name
      METADATA_TABLE = var.metadata_table_name
    }
  }

  tags = {
    Name = "${var.project_name}-read"
  }
}

resource "aws_lambda_function" "authorizer" {
  filename         = data.archive_file.auth_lambda_zip.output_path
  function_name    = "${var.project_name}-authorizer-${var.environment}"
  role             = var.lambda_role_arn
  handler          = "authorizer_handler.lambda_handler"
  source_code_hash = data.archive_file.auth_lambda_zip.output_base64sha256
  runtime          = "python3.9"

  environment {
    variables = {
      TOKEN_PARAM_NAME = var.token_param_name
    }
  }

  tags = {
    Name = "${var.project_name}-authorizer"
  }
}
data "archive_file" "notifier_lambda_zip" {
  type        = "zip"
  source_file = "${path.root}/lambda_src/realtime_notifier.py"
  output_path = "${path.module}/realtime_notifier.zip"
}

resource "aws_lambda_function" "notifier" {
  filename         = data.archive_file.notifier_lambda_zip.output_path
  function_name    = "${var.project_name}-notifier-${var.environment}"
  role             = var.lambda_role_arn
  handler          = "realtime_notifier.lambda_handler"
  source_code_hash = data.archive_file.notifier_lambda_zip.output_base64sha256
  runtime          = "python3.9"

  environment {
    variables = {
      APPSYNC_URL = var.appsync_url
    }
  }

  tags = {
    Name = "${var.project_name}-notifier"
  }
}

resource "aws_lambda_event_source_mapping" "dynamodb_stream" {
  event_source_arn  = var.dynamodb_stream_arn
  function_name     = aws_lambda_function.notifier.arn
  starting_position = "LATEST"
}

resource "aws_lambda_event_source_mapping" "sqs_ingest" {
  event_source_arn = var.sqs_queue_arn
  function_name    = aws_lambda_function.ingest.arn
  batch_size       = 10
}

