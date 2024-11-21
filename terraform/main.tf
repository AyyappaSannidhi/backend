provider "aws" {
  region = "us-east-1"
}

# Lambda Function resource
resource "aws_lambda_function" "sasss_backend" {
  function_name    = "sasss_backend"
  handler          = "app.handler"
  runtime          = "python3.12"
  role             = "arn:aws:iam::936944053839:role/lambda_execution_role"
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