"""
This is the place for all custom column formatters
"""
from flask import Markup, url_for, request

from project.server.models import Customer, ReferralPartner


def customer_formatter(view, context, model: Customer, name):
    """ Build a link column to a customer """
    if model.customer:
        m_str = "<a href='%s'>%s - %s</a>" % (
            url_for('customer.details_view', id=model.customer.id),
            model.customer.first_name,
            model.customer.last_name
        )
        return Markup(m_str)
    else:
        return "N/A"


def ref_formatter(view, context, model: ReferralPartner, name):
    if request:
        root = request.url_root.rstrip('/')
        full_link = root + model.ref_link
        return full_link
