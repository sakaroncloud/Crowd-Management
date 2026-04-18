resource "aws_dynamodb_table" "crowd_zones" {
  name         = "${var.project_name}-zones-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "zoneId"

  attribute {
    name = "zoneId"
    type = "S"
  }

  stream_enabled   = true
  stream_view_type = "NEW_IMAGE"

  tags = {
    Name = "${var.project_name}-zones"
  }
}

resource "aws_dynamodb_table" "crowd_metadata" {
  name         = "${var.project_name}-metadata-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "zoneId"

  attribute {
    name = "zoneId"
    type = "S"
  }

  tags = {
    Name = "${var.project_name}-metadata"
  }
}
