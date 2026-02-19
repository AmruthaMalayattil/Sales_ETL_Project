from confluent_kafka import Producer
import json
import time
import random

# 1. Configuration (Get these from your Confluent Cloud 'Connect' tab)
conf = {
    'bootstrap.servers': 'YOUR_SERVER_ENDPOINT',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanisms': 'PLAIN',
    'sasl.username': 'YOUR_API_KEY',
    'sasl.password': 'YOUR_API_SECRET'
}

producer = Producer(conf)


def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}]")


# 2. Simulate live sales data
items = ['laptop', 'mouse', 'monitor', 'keyboard']

print("Starting Kafka Producer... Press Ctrl+C to stop.")
try:
    while True:
        data = {
            "item": random.choice(items),
            "revenue": random.randint(100, 1000),
            "cost": random.randint(50, 500)
        }

        # Send data to the 'sales_events' topic
        producer.produce('sales_events', json.dumps(data).encode('utf-8'), callback=delivery_report)
        producer.flush()

        time.sleep(2)  # Send a sale every 2 seconds
except KeyboardInterrupt:
    print("Stopping...")