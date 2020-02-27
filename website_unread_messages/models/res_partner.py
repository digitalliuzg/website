##############################################################################
#
#    Author: Oy Tawasta OS Technologies Ltd.
#    Copyright 2019- Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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
from odoo import models

# 2. Known third party imports:
# 3. Odoo imports:

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


_logger = logging.getLogger(__name__)


class ResPartner(models.Model):

    # 1. Private attributes
    _inherit = "res.partner"

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration
    @api.model
    def get_portal_needaction_count(self):
        """
        Compute the number of needaction in portal of the current user.

        1) Search for the models that have set unread_messages_format.<model>
        (these are the "portal messages")
        2) Find messages that have one of these models
        """
        if self.env.user.partner_id:
            enabled_models = self.env["website.message.format"].search([])
            model_list = list()
            for rec in enabled_models:
                model_list.append(rec.res_model.model)

            self.env.cr.execute(
                """
                SELECT count(*) as needaction_count
                FROM mail_message_res_partner_needaction_rel
                R RIGHT JOIN mail_message
                M ON (M.id = R.mail_message_id)
                WHERE R.res_partner_id = %s
                AND M.model IN %s
                AND M.website_published = true
                AND (R.is_read = false OR R.is_read IS NULL)""",
                (self.env.user.partner_id.id, tuple(model_list)),
            )
            return self.env.cr.dictfetchall()[0].get("needaction_count")
        _logger.error("Call to needaction_count without partner_id")
        return 0

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
