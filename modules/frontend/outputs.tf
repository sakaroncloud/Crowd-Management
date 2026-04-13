output "cloudfront_url" {
  description = "The HTTPS URL of the CloudFront distribution"
  value       = "https://${aws_cloudfront_distribution.frontend.domain_name}"
}

output "cloudfront_id" {
  description = "The CloudFront distribution ID (for cache invalidation)"
  value       = aws_cloudfront_distribution.frontend.id
}

output "bucket_name" {
  description = "The S3 bucket name holding the built files"
  value       = aws_s3_bucket.frontend.id
}
