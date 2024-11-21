provider "aws" {
  region = "us-east-1"
}

# Lambda Function resource (without zip file)
resource "aws_lambda_function" "sasss_backend" {
  function_name    = "sasss_backend"
  handler          = "app.handler"
  runtime          = "python3.12"
  role             = "arn:aws:iam::936944053839:role/lambda_execution_role"
  filename         = "function.zip"  # Make sure to manually upload the zip later

  environment {
    variables = {
      ENV = "production"
    }
  }

  # This is a temporary workaround to allow creation of the function without zip for now
  lifecycle {
    create_before_destroy = true
  }
}

output "lambda_function_name" {
  value = aws_lambda_function.sasss_backend.function_name
}