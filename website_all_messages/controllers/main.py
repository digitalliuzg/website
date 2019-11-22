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

# 3. Odoo imports (openerp):
from odoo import http
from odoo.http import request

# 4. Imports from Odoo modules (rarely, and only if necessary):

# 5. Local imports in the relative form:

# 6. Unknown third party imports (One per line sorted and splitted in


class WebsiteAllMessagesController(http.Controller):

    @http.route(
        ['/all_messages', '/all_messages/page/<int:page>'],
        type='http',
        auth='user',
        website=True,
    )
    def all_messages(self, search='', page=1, **post):
        """
        Route to show list of all portal messages.

        :param search: Search query
        :param page: pager current page
        :param post: kwargs
        :return: rendered object
        """
        partner_id = request.env.user.partner_id.id
        message_model = request.env['mail.message']
        page_enabled = request.env['ir.config_parameter'].sudo().get_param(
            'website_all_messages.page')

        if not page_enabled or not partner_id:
            # Hide page if it's not enabled
            return request.render('website.404')

        # Recordset of read messages
        domain = [
            ('website_published', '=', True),
            ('needaction_partner_ids', '=', partner_id),
            ('website_url', '!=', False),
            '|',
            ('author_id', 'ilike', search),
            ('record_name', 'ilike', search),
        ]

        messages_count = message_model.search_count(domain)
        url = request.httprequest.path.split("/page")[0]
        total_count = messages_count
        pager_limit = 50
        pager = request.website.pager(
            url=url,
            total=total_count,
            page=page,
            step=pager_limit,
            scope=7,
            url_args=post
        )
        messages = message_model.sudo().search(
            domain,
            order="id DESC",
            limit=pager_limit,
            offset=pager['offset']
        )
        search_url = request.httprequest.path + ("?%s" % search)

        message_start = abs(50 - page * pager_limit) + 1
        message_end = total_count if total_count < page * \
            pager_limit else page * pager_limit
        visible = "{} - {} / {}".format(message_start,
                                        message_end, total_count)

        values = {
            'messages': messages,
            'pager': pager,
            'visible_messages': visible,
            'search_url': search_url,
            'current_search': search,
        }
        return request.render(
            'website_all_messages.all_messages',
            values
        )
