provider "aws" {
  region = "us-east-1"
}

resource "random_password" "rds_password" {
  length  = 10
  special = false
}

resource "aws_s3_bucket" "s3_bucket" {
  bucket = "nci-attendance-webapp"
  acl    = "private"
  force_destroy = true
  lifecycle {
    prevent_destroy = false
  }

  tags = {
    Name        = "Neeti bucket"
    Environment = "dev"
  }
  
}

resource "aws_iam_role" "nci_attendance_lambda" {
  name = "nci_attendance_lambda"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Action": "sts:AssumeRole",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Effect": "Allow",
      "Sid": ""
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "AWSLambdaBasicExecutionRole" {
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
  role       = aws_iam_role.nci_attendance_lambda.name
}

resource "aws_iam_role_policy_attachment" "SecretsManagerReadWrite" {
  policy_arn = "arn:aws:iam::aws:policy/SecretsManagerReadWrite"
  role       = aws_iam_role.nci_attendance_lambda.name
}

resource "aws_iam_role_policy_attachment" "AmazonS3FullAccess" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
  role       = aws_iam_role.nci_attendance_lambda.name
}

# Ref Hashicorp AWS RDS Document
# https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/db_instance
resource "aws_db_instance" "default" {
  allocated_storage    = 10
  engine               = "mysql"
  engine_version       = "8.0.20"
  instance_class       = "db.t3.micro"
  port                 = 3306
  name                 = "nci_app"
  username             = "admin"
  password             = random_password.rds_password.result
  skip_final_snapshot  = true
  deletion_protection  = false
  publicly_accessible = true //to access rds via internet
}

// Create Secrets step
resource "aws_secretsmanager_secret" "mysql_rds_credentials" {
  name = "mysql_rds_credentials"
  recovery_window_in_days = 0
}

// Insert mysql username/password/db endpoint
resource "aws_secretsmanager_secret_version" "mysql_rds_credentials" {
  secret_id     = aws_secretsmanager_secret.mysql_rds_credentials.id
  secret_string = <<EOF
{
  "username": "${aws_db_instance.default.username}",
  "password": "${random_password.rds_password.result}",
  "engine": "mysql",
  "host": "${aws_db_instance.default.endpoint}",
  "port": ${aws_db_instance.default.port},
  "dbname": "${aws_db_instance.default.name}"
}
EOF
}
