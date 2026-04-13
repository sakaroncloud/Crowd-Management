# Seed Data — Dev Zone Records
# Populates the DynamoDB table with realistic dummy data for testing
# Safe to remove before production deployment

locals {
  seed_zones = [
    {
      zoneId     = "ZONE-A1"
      crowdCount = 23
      status     = "Normal"
      action     = "No Action"
      lastUpdated = "2026-04-13T20:00:00Z"
    },
    {
      zoneId     = "ZONE-B2"
      crowdCount = 67
      status     = "Busy"
      action     = "Monitor closely"
      lastUpdated = "2026-04-13T20:00:00Z"
    },
    {
      zoneId     = "ZONE-C3"
      crowdCount = 95
      status     = "Critical"
      action     = "Restrict Entry / Redirect Flow"
      lastUpdated = "2026-04-13T20:00:00Z"
    },
    {
      zoneId     = "ZONE-D4"
      crowdCount = 12
      status     = "Normal"
      action     = "No Action"
      lastUpdated = "2026-04-13T20:00:00Z"
    },
    {
      zoneId     = "ZONE-E5"
      crowdCount = 54
      status     = "Busy"
      action     = "Monitor closely"
      lastUpdated = "2026-04-13T20:00:00Z"
    },
    {
      zoneId     = "ZONE-F6"
      crowdCount = 8
      status     = "Normal"
      action     = "No Action"
      lastUpdated = "2026-04-13T20:00:00Z"
    },
  ]
}

resource "aws_dynamodb_table_item" "seed_zones" {
  for_each   = { for z in local.seed_zones : z.zoneId => z }
  table_name = module.dynamodb.table_name
  hash_key   = "zoneId"

  item = jsonencode({
    zoneId      = { S = each.value.zoneId }
    crowdCount  = { N = tostring(each.value.crowdCount) }
    status      = { S = each.value.status }
    action      = { S = each.value.action }
    lastUpdated = { S = each.value.lastUpdated }
  })

  lifecycle {
    # Don't overwrite if the Lambda has updated the data live
    ignore_changes = [item]
  }
}
