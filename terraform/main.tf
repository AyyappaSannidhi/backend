provider "aws" {
  region = "us-east-1"
}

# Create an IAM Role for Lambda with a policy
resource "aws_iam_role" "lambda_execution_role" {
  name               = "lambda_execution_role"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action    = "sts:AssumeRole"
        Effect    = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })
}

# Attach Basic Execution Policy to IAM Role
resource "aws_iam_role_policy_attachment" "lambda_execution_policy" {
  role       = aws_iam_role.lambda_execution_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# Lambda Function resource
resource "aws_lambda_function" "sasss_backend" {
  function_name    = "sasss_backend"
  handler          = "app.handler"
  runtime          = "python3.12"
  role             = aws_iam_role.lambda_execution_role.arn  # Use the ARN of the IAM role here
  filename         = "function.zip"

  environment {
    variables = {
      ENV = "production"
    }
  }
}

output "lambda_function_name" {
  value = aws_lambda_function.sasss_backend.function_name
}