from project.common.tricoma_api import TricomaCustomer
from project.common.tricoma_client import extract_customers
from project.server.extensions import celery
from project.server.extensions import tricoma_client, tricoma_api
from project.server.models import Customer


@celery.task(bind=True, max_retries=3)
def fetch_customers(task):
    tricoma = tricoma_client
    raw_csv = tricoma.export_customers().text
    customers = extract_customers(raw_csv)
    return customers


@celery.task(name='register_customer', bind=True, max_retries=3)
def register_customer(task, customer: dict):
    api = tricoma_api
    c = Customer.deserialize(customer)
    tri_c = TricomaCustomer.from_db_model(c)
    c_id = api.register_customer(tri_c)
    return c_id
