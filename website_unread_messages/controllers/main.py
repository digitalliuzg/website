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
import json
import time
from datetime import datetime

from odoo import _
from odoo import http
from odoo.http import request

# 2. Known third party imports:
# 3. Odoo imports (openerp):

# 4. Imports from Odoo modules (rarely, and only if necessary):

# 5. Local imports in the relative form:

# 6. Unknown third party imports (One per line sorted and splitted in


class WebsiteUnreadMessagesController(http.Controller):
    @http.route(
        ["/new_messages"], type="json", auth="user", website=True, csrf=False,
    )
    def new_messages(self, **post):
        """
        Route to return info about how many new messages partner has in
        the appointments.

        Use cases:
            Hide "No new messages" if the message has been displayed once
            Show message if state changes
            60 second cooldown, if the message is not marked as read

        Returns:
            -1 if no messages and message doesn't have to be displayed
            0 if no messages and message WILL BE displayed
            > 0 if new messages
        """
        current_user = request.env.user
        partner = current_user.partner_id
        timestamp = request.session.get("messages_checked")
        no_messages = _("There aren't any new messages!")
        msg = ""
        is_enabled = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("website_unread_messages.notifications")
        )
        if is_enabled:
            page_enabled = (
                request.env["ir.config_parameter"]
                .sudo()
                .get_param("website_unread_messages.page")
            )
            # Count unread portal messages
            message_count = partner.sudo(current_user).get_portal_needaction_count()

            if timestamp:
                # Last new messages retrieved at timestamp
                timestamp_date = datetime.fromtimestamp(timestamp)
                difference = (datetime.now() - timestamp_date).seconds
                too_soon = True if difference < 60 else False

                if too_soon and message_count != 0:
                    # Do not display message if message was displayed
                    # in the last 60 seconds
                    return False
                elif message_count == 0:
                    # State changed to 'all messages are read'
                    request.session["messages_checked"] = None
            else:
                if message_count == 0:
                    # No timestamp == no messages, so state didn't change
                    return False

            if message_count != 0:
                # Save timestamp to prevent spam
                request.session["messages_checked"] = time.time()
                msg = _("You have ")

                if message_count > 1:
                    msg += _("%d new messages in discussions!") % message_count
                else:
                    msg += _("a new message in discussions!")
                if page_enabled:
                    # If unread messages page is enabled (system parameters)
                    msg = "<a href='%s'>%s</a>" % ("/unread_messages", msg)

        notification_class = "info" if msg else "success"
        values = {
            "msg": msg if msg else no_messages,
            "notification_class": notification_class,
            "is_enabled": is_enabled,
        }
        return json.dumps(values)

    @http.route(
        ["/unread_messages", "/unread_messages/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def unread_messages(self, search="", page=1, **post):
        """ Route to show list of unread messages """
        partner_id = request.env.user.partner_id.id
        message_model = request.env["mail.message"]
        page_enabled = (
            request.env["ir.config_parameter"]
            .sudo()
            .get_param("website_unread_messages.page")
        )

        if not page_enabled or not partner_id:
            # Hide page if it's not enabled
            return request.render("website.404")

        # Recordset of unread messages
        domain = [
            ("website_published", "=", True),
            ("needaction_partner_ids", "=", partner_id),
            ("website_url", "!=", False),
            "|",
            ("author_id", "ilike", search),
            ("record_name", "ilike", search),
            "&",
            ("notification_ids.res_partner_id", "=", partner_id),
            ("notification_ids.is_read", "=", False),
        ]
        messages_count = message_model.search_count(domain)
        url = "/unread_messages"
        total_count = messages_count
        pager_limit = 50
        pager = request.website.pager(
            url=url,
            total=total_count,
            page=page,
            step=pager_limit,
            scope=7,
            url_args=post,
        )
        messages = message_model.sudo().search(
            domain, order="id DESC", limit=pager_limit, offset=pager["offset"]
        )
        search_url = "/unread_messages?%s" % (search)

        message_start = abs(50 - page * pager_limit) + 1
        message_end = (
            total_count if total_count < page * pager_limit else page * pager_limit
        )
        visible = "{} - {} / {}".format(message_start, message_end, total_count)

        values = {
            "messages": messages,
            "pager": pager,
            "visible_messages": visible,
            "search_url": search_url,
            "current_search": search,
        }
        return request.render("website_unread_messages.unread_messages", values)
