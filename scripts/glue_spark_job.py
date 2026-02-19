import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job

# 1. Initialize Glue Context (This is the 'AWS version' of SparkSession)
args = getResolvedOptions(sys.argv, ['JOB_NAME'])
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# 2. Read from S3 (The "Bronze" layer we created with Terraform)
# REPLACE with your actual bucket name
input_path = "s3://proj2-de-tutorial-raw-data-bucket/data/sales.csv"
df = spark.read.option("header", "true").csv(input_path)

# 3. Transform (Exactly like your local code!)
from pyspark.sql.functions import col
refined_df = df.withColumn("revenue", col("revenue").cast("double")) \
               .withColumn("cost", col("cost").cast("double")) \
               .withColumn("profit", col("revenue") - col("cost"))

# 4. Write to Iceberg in S3 (The "Silver" layer)
# Glue 4.0 handles the Iceberg configs for you!
output_path = "s3://proj2-de-tutorial-raw-data-bucket/iceberg_warehouse/"

refined_df.writeTo("glue_catalog.sales_db.sales_iceberg") \
    .tableProperty("format-version", "2") \
    .createOrReplace()

job.commit()