# 1. Define the Provider
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = "us-west-2" # Or your preferred region
}

# 2. Create the S3 Bucket
resource "aws_s3_bucket" "data_lake_raw" {
  # S3 bucket names must be globally unique! 
  # Change 'yourname' to something unique.
  bucket = "proj2-de-tutorial-raw-data-bucket" 
}

# 2. The Ownership (Required by AWS recently for security)
resource "aws_s3_bucket_ownership_controls" "raw_owner" {
  bucket = aws_s3_bucket.data_lake_raw.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

# 3. The ACL (Private by default - DevSecOps Best Practice)
resource "aws_s3_bucket_acl" "raw_acl" {
  depends_on = [aws_s3_bucket_ownership_controls.raw_owner]

  bucket = aws_s3_bucket.data_lake_raw.id
  acl    = "private"
}

# 1. Create an IAM Role for Glue (The 'ID Badge' for the job)
resource "aws_iam_role" "glue_role" {
  name = "GlueJobRole"
  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Action = "sts:AssumeRole"
      Effect = "Allow"
      Principal = { Service = "glue.amazonaws.com" }
    }]
  })
}

# 2. Give Glue permission to touch S3 and logs
resource "aws_iam_role_policy_attachment" "glue_s3_access" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3FullAccess"
}

resource "aws_iam_role_policy_attachment" "glue_service_role" {
  role       = aws_iam_role.glue_role.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSGlueServiceRole"
}

# 3. Define the Glue Job
resource "aws_glue_job" "sales_etl" {
  name     = "sales-etl-spark-job"
  role_arn = aws_iam_role.glue_role.arn
  glue_version = "4.0" # This includes Spark 3.3 and Python 3
  
  command {
    script_location = "s3://${aws_s3_bucket.data_lake_raw.bucket}/scripts/glue_spark_job.py"
    python_version  = "3"
  }

  default_arguments = {
    "--datalake-formats" = "iceberg"
    "--conf"             = "spark.sql.catalog.glue_catalog=org.apache.iceberg.spark.SparkCatalog --conf spark.sql.catalog.glue_catalog.warehouse=s3://${aws_s3_bucket.data_lake_raw.bucket}/iceberg_warehouse/ --conf spark.sql.catalog.glue_catalog.catalog-impl=org.apache.iceberg.aws.glue.GlueCatalog"
  }
}



# 4. Add the Database (Crucial for Iceberg)
#resource "aws_glue_catalog_database" "sales_db" {
 # name = "sales_db"
#}

# 5. Update the Streaming Job
resource "aws_glue_job" "sales_streaming" {
  name              = "sales-streaming-job"
  role_arn          = aws_iam_role.glue_role.arn
  glue_version      = "4.0"
  worker_type       = "G.1X"
  number_of_workers = 2

  command {
    name            = "gluestreaming"
    script_location = "s3://${aws_s3_bucket.data_lake_raw.bucket}/scripts/glue_streaming_iceberg.py"
    python_version  = "3"
  }

  # THIS BLOCK WAS MISSING IN YOUR STREAMING JOB:
  default_arguments = {
    "--datalake-formats" = "iceberg"
    "--conf"             = "spark.sql.extensions=org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions --conf spark.sql.catalog.spark_catalog=org.apache.iceberg.spark.SparkCatalog --conf spark.sql.catalog.spark_catalog.warehouse=s3://proj2-de-tutorial-raw-data-bucket/iceberg-data/ --conf spark.sql.catalog.spark_catalog.catalog-impl=org.apache.iceberg.aws.glue.GlueCatalog"
  }
}

