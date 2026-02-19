🚀 AWS Data Lakehouse: Kafka, Spark, & Iceberg


📌 Overview

This project implements a real-time Data Lakehouse architecture on AWS. It ingests sales events from Confluent Kafka, processes them via AWS Glue (Spark Streaming), and stores them in Apache Iceberg format on Amazon S3 for ACID-compliant analytics via Amazon Athena.

🏗️ Architecture

Ingestion: Confluent Kafka (Real-time events)

Processing: AWS Glue / PySpark (Structured Streaming)

Table Format: Apache Iceberg (Time-travel & Atomic transactions)

Infrastructure: Terraform (IaC)

Analysis: Amazon Athena (SQL)

🛠️ How to Run

cd terraform && terraform apply

Start the local producer: python scripts/kafka_producer.py

Monitor the Glue Streaming job in AWS Console.

Query data in Athena: SELECT * FROM sales_db.sales_iceberg;
