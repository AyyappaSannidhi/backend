provider "aws" {
  region = "us-east-1"
}

# Lambda Layer for Dependencies
resource "aws_lambda_layer_version" "sasss_backend_layer" {
  layer_name          = "sasss_backend_dependencies"
  compatible_runtimes = ["python3.12"]

  # Use local-exec provisioner to install dependencies and zip them
  provisioner "local-exec" {
    command = <<EOT
      pip install -r requirements.txt -t python/
      zip -r dependencies.zip python/
    EOT
    working_dir = "${path.root}"  # Point to the root directory where requirements.txt is located
  }

  # Use the generated dependencies.zip file
  filename   = "dependencies.zip"
  source_code_hash = filebase64sha256("dependencies.zip")
}

# Lambda Function
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

  layers = [aws_lambda_layer_version.sasss_backend_layer.arn]  # Attach the layer to the Lambda function
}

# Attach Basic Execution Policy to IAM Role
resource "aws_iam_role_policy_attachment" "lambda_execution_policy" {
  role       = "lambda_execution_role"
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

output "lambda_function_name" {
  value = aws_lambda_function.sasss_backend.function_name
}

output "lambda_layer_arn" {
  value = aws_lambda_layer_version.sasss_backend_layer.arn
}