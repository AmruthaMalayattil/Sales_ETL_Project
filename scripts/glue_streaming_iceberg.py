import sys
from awsglue.transforms import *
from awsglue.utils import getResolvedOptions
from pyspark.context import SparkContext
from awsglue.context import GlueContext
from awsglue.job import Job
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StructField, StringType, DoubleType

# 1. Get Job Arguments
args = getResolvedOptions(sys.argv, ['JOB_NAME'])

# 2. Initialize Glue/Spark (Crucial: Use glueContext)
sc = SparkContext()
glueContext = GlueContext(sc)
spark = glueContext.spark_session
job = Job(glueContext)
job.init(args['JOB_NAME'], args)

# 3. Schema matching your Kafka Producer
schema = StructType([
    StructField("item", StringType()),
    StructField("revenue", DoubleType()),
    StructField("cost", DoubleType())
])

# 4. Read from Confluent Kafka
# Note: In Glue, we don't need .config() for JARs if using --datalake-formats
kafka_df = spark.readStream.format("kafka") \
    .option("kafka.bootstrap.servers", "YOUR_CONFLUENT_ENDPOINT") \
    .option("subscribe", "sales_events") \
    .option("kafka.security.protocol", "SASL_SSL") \
    .option("kafka.sasl.mechanism", "PLAIN") \
    .option("kafka.sasl.jaas.config", 'org.apache.kafka.common.security.plain.PlainLoginModule required username="YOUR_KEY" password="YOUR_PASSWORD";') \
    .option("startingOffsets", "latest") \
    .load()

# 5. Transform
streaming_df = kafka_df.selectExpr("CAST(value AS STRING)") \
    .select(from_json(col("value"), schema).alias("data")) \
    .select("data.*") \
    .withColumn("profit", col("revenue") - col("cost"))

# 6. Write to Iceberg
# The 'glue_catalog' prefix matches your Terraform --conf setting
query = streaming_df.writeStream \
    .format("iceberg") \
    .outputMode("append") \
    .trigger(processingTime='1 minute') \
    .option("checkpointLocation", "s3://proj2-de-tutorial-raw-data-bucket/checkpoints/streaming_job/") \
    .toTable("sales_db.sales_iceberg") # Updated: removed 'glue_catalog.'

query.awaitTermination()