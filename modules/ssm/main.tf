resource "random_password" "ingest_token" {
  length  = 32
  special = false
}

resource "aws_ssm_parameter" "ingest_token" {
  name        = "/${var.project_name}/${var.environment}/ingest_token"
  description = "Security token for crowd data ingestion"
  type        = "SecureString"
  value       = random_password.ingest_token.result

  tags = {
    Name = "${var.project_name}-ingest-token"
  }
}
