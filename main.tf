# Root Main Configuration

module "iam" {
  source       = "./modules/iam"
  project_name = var.project_name
  dynamodb_arn = module.dynamodb.table_arn
  metadata_arn = module.dynamodb.metadata_table_arn
  s3_arn       = module.s3.bucket_arn
  sns_arn      = module.sns.topic_arn
}

module "dynamodb" {
  source       = "./modules/dynamodb"
  project_name = var.project_name
  environment  = var.environment
}

module "s3" {
  source       = "./modules/s3"
  project_name = var.project_name
  environment  = var.environment
}

module "sns" {
  source       = "./modules/sns"
  project_name = var.project_name
  environment  = var.environment
}

module "cognito" {
  source       = "./modules/cognito"
  project_name = var.project_name
  environment  = var.environment
  frontend_url = module.frontend.cloudfront_url
}

module "ssm" {
  source       = "./modules/ssm"
  project_name = var.project_name
  environment  = var.environment
}

module "appsync" {
  source                = "./modules/appsync"
  project_name          = var.project_name
  environment           = var.environment
  aws_region            = var.aws_region
  user_pool_id          = module.cognito.user_pool_id
  appsync_logs_role_arn = module.iam.appsync_logs_role_arn
  read_handler_arn      = module.lambda.read_lambda_arn
  lambda_role_arn       = module.iam.lambda_role_arn
}


module "lambda" {
  source              = "./modules/lambda"
  project_name        = var.project_name
  environment         = var.environment
  lambda_role_arn     = module.iam.lambda_role_arn
  dynamodb_table_name  = module.dynamodb.table_name
  metadata_table_name  = module.dynamodb.metadata_table_name
  s3_bucket_name       = module.s3.bucket_name
  sns_topic_arn        = module.sns.topic_arn
  token_param_name     = module.ssm.parameter_name
  appsync_url          = module.appsync.graphql_api_url
  dynamodb_stream_arn  = module.dynamodb.stream_arn
}


module "api_gateway" {
  source                   = "./modules/api_gateway"
  project_name             = var.project_name
  environment              = var.environment
  ingest_lambda_arn        = module.lambda.ingest_lambda_arn
  read_lambda_arn          = module.lambda.read_lambda_arn
  ingest_lambda_invoke_arn = module.lambda.ingest_lambda_invoke_arn
  read_lambda_invoke_arn   = module.lambda.read_lambda_invoke_arn
  ingest_lambda_name       = module.lambda.ingest_lambda_name
  read_lambda_name         = module.lambda.read_lambda_name
  user_pool_id             = module.cognito.user_pool_id
  user_pool_arn            = module.cognito.user_pool_arn
  user_pool_client_id      = module.cognito.user_pool_client_id
  auth_lambda_arn          = module.lambda.auth_lambda_arn
  auth_lambda_invoke_arn   = module.lambda.auth_lambda_invoke_arn
}

module "monitoring" {
  source             = "./modules/monitoring"
  project_name       = var.project_name
  environment        = var.environment
  ingest_lambda_name = module.lambda.ingest_lambda_name
  read_lambda_name   = module.lambda.read_lambda_name
  api_id             = module.api_gateway.api_id
  sns_topic_arn      = module.sns.topic_arn
  tags               = var.tags
}

module "frontend" {
  source       = "./modules/frontend"
  project_name = var.project_name
  environment  = var.environment
  ui_dist_path = "${path.root}/dashboard/dist"
}


