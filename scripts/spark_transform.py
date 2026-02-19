from pyspark.sql import SparkSession
from pyspark.sql.functions import col
from pathlib import Path
import os
import sys

# --- THE WINDOWS FIX ---
# Tell Spark explicitly where your winutils.exe is
os.environ["HADOOP_HOME"] = "C:\\hadoop"
sys.path.append("C:\\hadoop\\bin")

# --- THE PATH FIXER ---
# This finds the 'sales_etl_project' root folder
base_path = Path(__file__).resolve().parent.parent
csv_path = str(base_path / "data" / "sales.csv")
# 1. Initialize Spark
#spark = SparkSession.builder.appName("SalesTransformation").master("local[*]").getOrCreate()

spark = SparkSession.builder \
    .appName("IcebergLab") \
    .master("local[*]") \
    .config("spark.jars.packages", "org.apache.iceberg:iceberg-spark-runtime-3.3_2.12:1.1.0") \
    .config("spark.sql.extensions", "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions") \
    .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog") \
    .config("spark.sql.catalog.local.type", "hadoop") \
    .config("spark.sql.catalog.local.warehouse", "data/iceberg_warehouse") \
    .getOrCreate()



# 2. Read the CSV (Spark can read local or S3)
# Note: Spark infers the schema (detects numbers vs strings)
df = spark.read.option("header", "true").csv(csv_path)

# 3. Transformation (The Spark Way)
# We don't use loops. We use "Transformations" on the whole column.
refined_df = df.withColumn("revenue", col("revenue").cast("double")) \
               .withColumn("cost", col("cost").cast("double")) \
               .withColumn("profit", col("revenue") - col("cost"))

# 4. Show the results on terminal
#refined_df.select("item", "profit").show()


# 4. Save as Parquet
output_path = str(base_path / "data" / "refined_sales.parquet")

print(f"Saving Parquet to: {output_path}")
refined_df.write.mode("overwrite").parquet(output_path)

# Create the table
refined_df.writeTo("local.db.sales_iceberg").createOrReplace()

# 5. Read it back to prove it works
parquet_df = spark.read.parquet(output_path)
parquet_df.show()

# 5. Stop the session
spark.stop()