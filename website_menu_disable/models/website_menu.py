from odoo import fields
from odoo import models


class WebsiteMenu(models.Model):

    _inherit = "website.menu"

    active = fields.Boolean(default=True,)
