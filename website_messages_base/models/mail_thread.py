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

# 2. Known third party imports:

# 3. Odoo imports:
from odoo import api, models

# 4. Imports from Odoo modules:

# 5. Local imports in the relative form:

# 6. Unknown third party imports:


class MailThread(models.AbstractModel):

    # 1. Private attributes
    _inherit = 'mail.thread'

    # 2. Fields declaration

    # 3. Default methods

    # 4. Compute and search fields, in the same order that fields declaration

    # 5. Constraints and onchanges

    # 6. CRUD methods

    # 7. Action methods

    # 8. Business methods
    @api.multi
    def mark_portal_messages_read(self):
        """
        Mark messages read for the current partner.

        :return: list of message IDs
        """
        partner_id = self.env.user.partner_id.id
        domain = [
            ('model', '=', self._name),
            ('res_id', 'in', self.ids),
            ('website_published', '=', True),
            ('notification_ids.res_partner_id', '=', partner_id),
            ('notification_ids.is_read', '=', False),
        ]
        messages = self.env['mail.message'].sudo().search(domain)
        notifications = self.env['mail.notification'].sudo().search([
            ('mail_message_id', 'in', messages.ids),
            ('res_partner_id', '=', partner_id),
            ('is_read', '=', False),
        ])
        notifications.write({'is_read': True})
        return messages.ids
