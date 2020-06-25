from flask import current_app

from project.server.common.tricoma_api import TricomaCustomer
from project.server.common.tricoma_client import extract_customers
from project.server.extensions import celery
from project.server.extensions import tricoma_client, tricoma_api
from project.server.models import Customer


def register_tricoma_if_enabled(customer):
    """ Register the customer on tricoma if TRICOMA_API_URL and is set """
    conf = current_app.config
    if conf.get("TRICOMA_API_URL") and conf.get("REGISTER_CUSTOMER_IN_TRICOMA"):
        try:
            register_customer.apply_async(args=(customer.serialize(),))
        except Exception as e:
            current_app.logger.error(e)


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
