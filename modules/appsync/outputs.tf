output "graphql_api_url" {
  value = aws_appsync_graphql_api.crowdsync.uris["GRAPHQL"]
}

output "graphql_api_id" {
  value = aws_appsync_graphql_api.crowdsync.id
}
