provider "aws" {
  region = "us-east-1"  # Change as needed
}

# Create Lambda Layer for Dependencies
resource "aws_lambda_layer_version" "dependencies_layer" {
  filename           = "dependencies.zip" # Pre-zipped dependencies
  layer_name         = "sasss_backend_dependencies"
  compatible_runtimes = ["python3.12"]

  lifecycle {
    create_before_destroy = true
  }
}

# Create Lambda Function
resource "aws_lambda_function" "sasss_backend" {
  function_name    = "sasss_backend"
  handler          = "app.handler"
  runtime          = "python3.12"
  role             = aws_iam_role.lambda_execution_role.arn
  filename         = "function.zip" # Pre-zipped Lambda deployment package
  layers           = [aws_lambda_layer_version.dependencies_layer.arn]

  lifecycle {
    create_before_destroy = true
  }

  environment {
    variables = {
      ENV = "production"
    }
  }
}

# Create IAM Role for Lambda
resource "aws_iam_role" "lambda_execution_role" {
  name = "lambda_execution_role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = { Service = "lambda.amazonaws.com" }
      }
    ]
  })
}

# Attach Basic Execution Role
resource "aws_iam_role_policy_attachment" "lambda_execution_policy" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# # Create DynamoDB Access Policy
# resource "aws_iam_policy" "dynamodb_access_policy" {
#   name        = "DynamoDBAccessPolicy"
#   description = "Policy for Lambda to access DynamoDB tables"
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action   = [
#           "dynamodb:PutItem",
#           "dynamodb:GetItem",
#           "dynamodb:UpdateItem",
#           "dynamodb:DeleteItem",
#           "dynamodb:Query",
#           "dynamodb:Scan"
#         ]
#         Effect   = "Allow"
#         Resource = "arn:aws:dynamodb:us-east-1:*:table/*" # Adjust region and resource
#       }
#     ]
#   })
# }

# # Attach DynamoDB Access Policy to Role
# resource "aws_iam_role_policy_attachment" "dynamodb_policy_attachment" {
#   role       = aws_iam_role.lambda_execution_role.name
#   policy_arn = aws_iam_policy.dynamodb_access_policy.arn
# }

# # Create S3 Access Policy
# resource "aws_iam_policy" "s3_access_policy" {
#   name        = "S3AccessPolicy"
#   description = "Policy for Lambda to access S3"
#   policy = jsonencode({
#     Version = "2012-10-17"
#     Statement = [
#       {
#         Action   = [
#           "s3:GetObject",
#           "s3:PutObject",
#           "s3:DeleteObject",
#           "s3:ListBucket"
#         ]
#         Effect   = "Allow"
#         Resource = [
#           "arn:aws:s3:::your-bucket-name", # Replace with your bucket name
#           "arn:aws:s3:::your-bucket-name/*"
#         ]
#       }
#     ]
#   })
# }

# # Attach S3 Access Policy to Role
# resource "aws_iam_role_policy_attachment" "s3_policy_attachment" {
#   role       = aws_iam_role.lambda_execution_role.name
#   policy_arn = aws_iam_policy.s3_access_policy.arn
# }

# Outputs
output "lambda_function_name" {
  value = aws_lambda_function.sasss_backend.function_name
}