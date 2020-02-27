from openerp import fields
from openerp import models


class PaymentAcquirer(models.Model):
    _inherit = "payment.acquirer"

    website_show_company = fields.Boolean(
        string="Visible for companies (website)", default=True,
    )

    website_show_private = fields.Boolean(
        string="Visible for private customers (website)", default=True,
    )
