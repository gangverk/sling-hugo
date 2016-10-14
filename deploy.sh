#!/bin/bash

echo "Deploying sling-hugo ..."

aws s3 sync ./_build s3://getsling-blog --region=us-east-1 --acl=public-read --exclude "index.html"  --exclude "404.html" --exclude ".git/*" "${@:2}"
aws s3 sync ./_build s3://getsling-blog --region=us-east-1 --acl=public-read --exclude "*" --include "index.html"  --include "404.html" --delete --cache-control="no-cache, no-store" "${@:2}"