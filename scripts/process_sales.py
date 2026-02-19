import csv
import boto3  # New: AWS SDK for Python
from pathlib import Path
from io import StringIO


def upload_to_s3(content, bucket_name, file_name):
    s3 = boto3.client('s3')
    try:
        s3.put_object(Bucket=bucket_name, Key=file_name, Body=content)
        print(f"Successfully uploaded {file_name} to {bucket_name}")
    except Exception as e:
        print(f"Upload failed: {e}")


def calculate_sales_profit():
    base_path = Path(__file__).resolve().parent.parent
    data_path = base_path / "data" / "sales.csv"

    # We will store our output in a "Buffer" (memory) before sending to S3
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(['item', 'profit'])  # Header

    with open(data_path, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            try:
                item = row['item']
                profit = float(row['revenue']) - float(row['cost'])
                writer.writerow([item, profit])
            except ValueError:
                continue

    # Send the buffer content to S3
    bucket_name = "proj2-de-tutorial-raw-data-bucket"  # MUST match your Terraform name
    upload_to_s3(output.getvalue(), bucket_name, "refined_sales/profit_report.csv")


if __name__ == "__main__":
    calculate_sales_profit()