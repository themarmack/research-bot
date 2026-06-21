# Deliberately bad Terraform for iac-security-reviewer acceptance test.
# Every issue is intentional. See SKILL.md for expected findings.

# BANK-IAC-001: provider block doesn't declare region — bad
# (relying on provider default at apply-time = residency audit gap)
provider "aws" {
  # region intentionally omitted
}

# BANK-IAC-002 + BANK-IAC-007: no encryption at rest; no versioning
resource "aws_s3_bucket" "payments_data" {
  bucket = "payments-data-bucket"
  # BANK-IAC-003: required tags missing
}

# CKV_AWS_18: no logging configured for the bucket
# (standard checkov rule reference)

# BANK-IAC-004: public ingress on a non-edge resource
resource "aws_security_group" "payments_sg" {
  name = "payments-sg"

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# BANK-IAC-005 + BANK-IAC-008: AWS-managed key; backups not declared
resource "aws_db_instance" "payments_db" {
  identifier        = "payments-db"
  engine            = "postgres"
  instance_class    = "db.t3.medium"
  allocated_storage = 100

  # storage_encrypted defaults vary; not declared → BANK-IAC-002
  # kms_key_id not specified → BANK-IAC-005
  # backup_retention_period not declared → BANK-IAC-008
  # BANK-IAC-003: required tags missing
}

# BANK-IAC-006: wildcard IAM
resource "aws_iam_policy" "payments_app_policy" {
  name = "payments-app-policy"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect   = "Allow"
      Action   = "*"
      Resource = "*"
    }]
  })
}

# BANK-IAC-009: runtime = "latest"
resource "aws_lambda_function" "payments_processor" {
  function_name = "payments-processor"
  role          = aws_iam_role.example.arn
  handler       = "index.handler"
  runtime       = "nodejs-latest"  # bad

  # BANK-IAC-003: required tags missing
}

resource "aws_iam_role" "example" {
  name = "example"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = { Service = "lambda.amazonaws.com" }
      Action = "sts:AssumeRole"
    }]
  })
}
