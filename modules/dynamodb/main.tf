resource "aws_dynamodb_table" "crowd_zones" {
  name         = "${var.project_name}-zones-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "zoneId"

  attribute {
    name = "zoneId"
    type = "S"
  }

  tags = {
    Name = "${var.project_name}-zones"
  }
}
