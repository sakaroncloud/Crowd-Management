resource "random_string" "cognito_domain_prefix" {
  length  = 8
  special = false
  upper   = false
}

resource "aws_cognito_user_pool" "pool" {
  name = "${var.project_name}-user-pool-${var.environment}"

  username_attributes      = ["email"]
  auto_verified_attributes = ["email"]

  password_policy {
    minimum_length    = 8
    require_lowercase = true
    require_numbers   = true
    require_symbols   = true
    require_uppercase = true
  }

  verification_message_template {
    default_email_option = "CONFIRM_WITH_CODE"
    email_subject        = "CrowdSync Verification Code"
    email_message        = "Your verification code for CrowdSync is {####}. Please enter this code in the app to complete your registration."
  }

  schema {
    attribute_data_type = "String"
    name                = "email"
    required            = true
    mutable             = true
  }


  admin_create_user_config {
    allow_admin_create_user_only = true
  }


  account_recovery_setting {
    recovery_mechanism {
      name     = "verified_email"
      priority = 1
    }
  }

  tags = {
    Name = "${var.project_name}-user-pool"
  }
}

resource "aws_cognito_user_pool_client" "client" {
  name = "${var.project_name}-client-${var.environment}"

  user_pool_id = aws_cognito_user_pool.pool.id

  # PKCE configuration: No client secret, allow auth code flow
  generate_secret     = false
  explicit_auth_flows = [
    "ALLOW_USER_PASSWORD_AUTH",
    "ALLOW_REFRESH_TOKEN_AUTH",
    "ALLOW_USER_SRP_AUTH"
  ]

  supported_identity_providers = ["COGNITO"]
  allowed_oauth_flows_user_pool_client = true
  allowed_oauth_flows                  = ["code"]
  allowed_oauth_scopes                 = ["email", "openid", "profile"]
  callback_urls                        = compact(["http://localhost:3000", "http://localhost:5173", var.frontend_url])
  logout_urls                          = compact(["http://localhost:3000", "http://localhost:5173", var.frontend_url])

  prevent_user_existence_errors = "ENABLED"
}


resource "aws_cognito_user_pool_domain" "main" {
  domain       = "${var.project_name}-${random_string.cognito_domain_prefix.result}"
  user_pool_id = aws_cognito_user_pool.pool.id
}

resource "aws_cognito_user" "admin_seed" {
  user_pool_id = aws_cognito_user_pool.pool.id
  username     = "sakaroncloud@gmail.com"

  attributes = {
    email          = "sakaroncloud@gmail.com"
    email_verified = true
  }

  # Cognito will send a temporary password to this email
  desired_delivery_mediums = ["EMAIL"]
  
  # Ensure we don't accidentally recreate the user if attributes change slightly
  lifecycle {
    ignore_changes = [attributes]
  }
}

