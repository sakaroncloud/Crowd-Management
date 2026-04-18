output "web_acl_arn" {
  description = "The ARN of the Global WAF Web ACL (for CloudFront)"
  value       = aws_wafv2_web_acl.main.arn
}

output "regional_web_acl_arn" {
  description = "The ARN of the Regional WAF Web ACL (for API Gateway)"
  value       = aws_wafv2_web_acl.regional.arn
}
