##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2019- Oy Tawasta OS Technologies Ltd. (http://www.tawasta.fi)
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program. If not, see http://www.gnu.org/licenses/agpl.html
#
##############################################################################
# 1. Standard library imports:
import logging

from odoo import api
from odoo import fields
from odoo import models

# 2. Known third party imports:
# 3. Odoo imports (openerp):

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:

_logger = logging.getLogger(__name__)


class ResConfigSettings(models.TransientModel):

    # 1. Private attributes
    _inherit = "res.config.settings"

    # 2. Fields declaration
    all_messages_page = fields.Boolean(
        string="All messages' page", help="Enable all messages' page on website",
    )

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods
    @api.model
    def get_values(self):
        res = super(ResConfigSettings, self).get_values()
        all_messages_page = (
            self.env["ir.config_parameter"]
            .sudo()
            .get_param("website_all_messages.page", False)
        )
        res.update(all_messages_page=all_messages_page,)
        return res

    @api.multi
    def set_values(self):
        super(ResConfigSettings, self).set_values()
        self.env["ir.config_parameter"].sudo().set_param(
            "website_all_messages.page", self.all_messages_page
        )

    # 7. Action methods

    # 8. Business methods
