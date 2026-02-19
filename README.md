# 🚀 AWS Data Lakehouse: Kafka, Spark, & Iceberg

## 📌 Overview
This project implements a real-time **Data Lakehouse** architecture on AWS. It ingests sales events from **Confluent Kafka**, processes them via **AWS Glue (Spark Streaming)**, and stores them in **Apache Iceberg** format on **Amazon S3** for ACID-compliant analytics via **Amazon Athena**.

---

## 🏗️ Architecture
* **Ingestion:** Confluent Kafka (Real-time events)
* **Processing:** AWS Glue / PySpark (Structured Streaming)
* **Table Format:** Apache Iceberg (Time-travel & Atomic transactions)
* **Infrastructure:** Terraform (IaC)
* **Analysis:** Amazon Athena (SQL)



---

## 🛠️ How to Run

1.  **Deploy Infrastructure**
    ```bash
    cd terraform && terraform apply
    ```

2.  **Start Producer**
    Start the local producer to begin streaming events:
    ```bash
    python scripts/kafka_producer.py
    ```

3.  **Monitor Job**
    Monitor the **Glue Streaming** job in the AWS Console.

4.  **Query Data**
    Run the following in **Amazon Athena**:
    ```sql
    SELECT * FROM sales_db.sales_iceberg;
    ```
