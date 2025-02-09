import logging
import watchtower
import boto3
import os

def setup_cloudwatch_logger():
    LOG_GROUP = "Expedite-Commerce-Feedback-Analysis"
    LOG_STREAM = "Expedite-Commerce-Feedback-Analysis-Stream"

    client_logs = boto3.client(
        "logs",
        region_name="us-east-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
    )

    logger = logging.getLogger("cloudwatch_logger")
    logger.setLevel(logging.INFO)

    # Clear any existing handlers
    logger.handlers.clear()

    cloudwatch_handler = watchtower.CloudWatchLogHandler(
        log_group=LOG_GROUP,
        stream_name=LOG_STREAM,
        boto3_client=client_logs,
        send_interval=1,
        create_log_group=False  # Add this to prevent creation attempts
    )

    formatter = logging.Formatter('%(asctime)s : %(levelname)s - %(message)s')
    cloudwatch_handler.setFormatter(formatter)

    logger.addHandler(cloudwatch_handler)
    return logger, cloudwatch_handler