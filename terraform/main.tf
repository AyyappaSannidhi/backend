provider "aws" {
  region = "us-east-1"
}

# Lambda Function without the layer (Handled in the deploy.yml file)
resource "aws_lambda_function" "sasss_backend" {
  function_name    = "sasss_backend"
  handler          = "app.handler"
  runtime          = "python3.12"
  role             = aws_iam_role.lambda_execution_role.arn
  filename         = "function.zip"

  environment {
    variables = {
      ENV = "production"
    }
  }
}

# Attach Basic Execution Policy to IAM Role
resource "aws_iam_role_policy_attachment" "lambda_execution_policy" {
  role       = "lambda_execution_role"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

output "lambda_function_name" {
  value = aws_lambda_function.sasss_backend.function_name
}
