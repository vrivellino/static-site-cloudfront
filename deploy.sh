#!/usr/bin/env bash
set -e

set -o allexport
source .config
set +o allexport

echo 'Packaging lambda-sam.yaml to lambda-cfn.yaml...'
aws cloudformation package \
    --template-file lambda-sam.yaml \
    --s3-bucket $s3_bucket \
    --s3-prefix $s3_prefix \
    --output-template-file lambda-cfn.yaml
echo

echo 'Deploying cf-lambda ...'
aws cloudformation deploy \
    --stack-name cf-lambda \
    --template-file lambda-cfn.yaml \
    --no-fail-on-empty-changeset
echo

lambda_ver_arn=$(aws cloudformation describe-stack-resources --stack-name cf-lambda --query 'StackResources[?ResourceType==`AWS::Lambda::Version`].PhysicalResourceId' --output=text)

echo "Deploying cf-distribution ..."
aws cloudformation deploy \
    --stack-name cf-distribution \
    --template-file distribution.yaml \
    --parameter-overrides \
        "CloudfrontLoggingBucket=$cf_logging_bucket" \
        "CloudfrontLoggingPrefix=$cf_logging_prefix" \
        "LambdaFnArn=$lambda_ver_arn" \
        "SslCommonName=$cf_ssl_cn" \
        "SslDomainName=$cf_ssl_dom" \
        "SslDomainZoneId=$cf_ssl_zid" \
    --no-fail-on-empty-changeset

static_s3_bucket="$(aws cloudformation describe-stacks \
    --stack-name cf-distribution --output=text \
    --query 'Stacks[0].Outputs[?"OutputKey"==`S3Bucket`].OutputValue')"
echo

echo "Syncing static-site/ to s3://$static_s3_bucket/"
aws s3 sync --cache-control 'public, max-age=1800' static-site/ "s3://$static_s3_bucket/"
