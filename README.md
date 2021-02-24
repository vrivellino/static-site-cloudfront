# static-site-cloudfront

A static website hosted in S3 &amp; CloudFront with a Lambda@Edge PoC

This repo provides a barebones structure for hosting a static website in S3 fronted with a Cloudfront
distribution.

Included in this proof-of-concept is a Lambda@Edge function that responds at the endpoint `/api/echo`

## Requirements
- awscli installed and configured
- existing S3 bucket for Lambda deployment package
- IAM credentials with permissions to deploy Cloudformation, S3, Lambda, and Cloudfront resources

## Files

- `deploy.sh`: Bash script that deploys the Cloudformation stacks (`cf-lambda` and `cf-distribution`) and
    syncs `static-site/` to the S3 bucket created in cf-distribution
- `.config.example`: Example config file that needs to be copied to `.config` and populated with your values
- `app/`: Directory containing Lambda@Edge handler
- `lambda-sam.yaml`: AWS Serverless Application Model template for Lambda function that will get deployed to
    Lambda@Edge
- `distribution.yaml`: Cloudformation template that deploys S3 bucket and Cloudfront distribution
- `static-site/`: Static website files that gets synced to static bucket

## Configuration

Populate `.config` with the following values:

- `s3_bucket`: _REQUIRED_ S3 bucket for lambda deployment packages. deploy.sh will upload zip files here
- `s3_prefix`: Object prefix for lambda deployment packages. Empty string will place objects at root of s3_bucket

- `cf_logging_bucket` and `cf_logging_prefix`: Optional S3 bucket & prefix to pass to Cloudfront distribution
    config that will enable the distribution's request logging. This bucket must already exist and have proper
    ACLs and/or bucket policy for Cloudfront log delivery
- `cf_ssl_cn`: Optional common name for ssl certificate. When set, an ACM certificate will be provisioned via
    distribution.yaml
- `cf_ssl_dom`: Domain name used for validation of ssl common name
- `cf_ssl_zid`: Route53 Zone identifier of ssl common name's domain. If set, Cloudformation will attempt to
    validate via DNS. When not set, email verification will be used

## Deployment

Execute `./deploy.sh` after configuring
