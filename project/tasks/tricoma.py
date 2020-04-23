from project.common.tricoma_client import extract_customers
from project.server.extensions import celery
from project.server.extensions import tricoma_client


@celery.task(bind=True, max_retries=5)
def fetch_customers(task):
    tricoma = tricoma_client
    raw_csv = tricoma.export_customers().text
    customers = extract_customers(raw_csv)
    return customers
