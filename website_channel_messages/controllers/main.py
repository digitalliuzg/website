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
import os
from PIL import Image
from io import BytesIO
import base64
import logging
from datetime import datetime

# 2. Known third party imports:

# 3. Odoo imports (openerp):
from odoo import http
from odoo.http import request
from odoo.tools import image_save_for_web

# 4. Imports from Odoo modules (rarely, and only if necessary):

# 5. Local imports in the relative form:

# 6. Unknown third party imports (One per line sorted and splitted in

_logger = logging.getLogger(__name__)


def compress_image(image):
    """
    Function to compress image accordingly.
    This function uses image_save_for_web-utility from tools.
    Max dimensions can be set on system parameters.
    Process of compressing image:
    - Calculate new image dimensions according to MAX_WIDTH and MAX_HEIGHT
    - Resize image with new dimensions
    - Compress using image_save_for_web -utility

    TODO: Fix MAX_WIDTH and MAX_HEIGHT to be fetched from ir.config_parameter

    :param image: Image data in binary
    :return: Compressed and resized image data in binary
    """
    MAX_WIDTH = 1080
    MAX_HEIGHT = 1080
    img = Image.open(BytesIO(image))
    (width, height) = img.size
    _logger.debug("Image starting size: (%s, %s)" % (width, height))
    if width > MAX_WIDTH or height > MAX_HEIGHT:
        if width > height:
            if width > MAX_WIDTH:
                new_height = int(round((MAX_WIDTH / float(width)) * height))
                new_width = MAX_WIDTH
        else:
            if height > MAX_HEIGHT:
                new_width = int(round((MAX_HEIGHT / float(height)) * width))
                new_height = MAX_HEIGHT
        img.thumbnail((new_width, new_height), Image.ANTIALIAS)
        _logger.debug("Compressed size: (%s, %s)" % (new_width, new_height))
    return image_save_for_web(img)


def process_file(file):
    """
    Check if the file is too large.
    Max size can be set on system parameters.
    TODO: Fix MAX_SIZE to be fetched from ir.config_parameter

    :param file: processed file
    :return: boolean if the file was too big
    """
    MAX_SIZE = 20
    too_big = False
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_SIZE * 1024 * 1024:
        too_big = True
        _logger.warning("Attachment filesize too big: %d MB" %
                        (file_size / 1024 / 1024))
    return too_big


def process_message(user, record, data):
    """
    Process message posted to record:
    - Compress and resize image
    - Check that the attachment isn"t too big
    - Notify related partners
    :param user: current user
    :param record: related record
    :param data: submitted form data
    """
    comment = data.get("comment")
    image = data.get("resized") or data.get("image")
    file = data.get("file")
    attachment_list = list()
    error = False
    if comment:
        if image:
            if data.get("resized"):
                img_string = data.get("resized").split(",")[1]
                image_data = base64.b64decode(img_string)
            else:
                image_data = image.read()
            resized = compress_image(image_data)
            mimetype = data.get("image").mimetype
            filename = data.get(
                "image").filename if "png" not in mimetype else "image.jpg"
            attachment_list.append((filename, resized))
        if file:
            too_big = process_file(file)
            if too_big:
                error = True
            file_data = file.read()
            attachment_list.append((file.filename, file_data))
        if not error:
            notified_partner_ids = record.channel_last_seen_partner_ids.mapped(
                "partner_id").ids
            record.sudo().message_post(
                author_id=user.partner_id.id,
                body=comment,
                message_type="comment",
                subtype="mail.mt_comment",
                attachments=attachment_list,
                partner_ids=notified_partner_ids,
            )


class WebsiteChannelMessagesController(http.Controller):

    @http.route(
        ["/website_channel", "/website_channel/page/<int:page>"],
        type="http",
        auth="user",
        website=True,
    )
    def website_channels(self, search="", page=1, **post):
        """
        Route to show list of all channels.

        :param search: Search query
        :param page: pager current page
        :param post: kwargs
        :return: rendered object
        """
        partner_id = request.env.user.partner_id.id
        channel_model = request.env["mail.channel"]

        if not partner_id:
            return request.render("website.404")

        domain = [
            ("public", "=", "private"),
            ("channel_partner_ids", "in", [partner_id]),
            "|",
            ("name", "ilike", search),
            ("channel_partner_ids", "ilike", search),
        ]
        channel_count = channel_model.search_count(domain)
        url = request.httprequest.path.split("/page")[0]
        total_count = channel_count
        pager_limit = 50
        pager = request.website.pager(
            url=url,
            total=total_count,
            page=page,
            step=pager_limit,
            scope=7,
            url_args=post
        )
        channels = channel_model.sudo().search(
            domain,
            limit=pager_limit,
            offset=pager["offset"]
        ).sorted(key=lambda r: r.channel_message_ids.ids, reverse=True)

        search_url = request.httprequest.path + ("?%s" % search)
        message_start = abs(50 - page * pager_limit) + 1
        message_end = total_count if total_count < page * pager_limit \
            else page * pager_limit
        visible = "{} - {} / {}".format(message_start, message_end, total_count)

        partners = request.env["res.users"].sudo().search([
            ('partner_id', '!=', partner_id)
        ]).mapped('partner_id')
        values = {
            "channels": channels,
            "pager": pager,
            "visible_channels": visible,
            "search_url": search_url,
            "current_search": search,
            "partners": partners,
        }
        return request.render(
            "website_channel_messages.my_channels",
            values
        )

    @http.route(
        ["/website_channel/<int:channel_id>"],
        type="http",
        auth="user",
        website=True,
    )
    def channel_messages(self, channel_id=None, **post):
        """
        Route to show list of all channels.

        :param channel_id: Related channel ID
        :param post: kwargs
        :return: rendered object
        """
        user = request.env.user
        channel = request.env["mail.channel"].sudo().search([
            ("id", "=", channel_id),
            ("public", "=", "private"),
            ("channel_partner_ids", "in", [user.partner_id.id]),
        ])

        if not channel:
            return request.render("website.404")

        channel.sudo(user).mark_portal_messages_read()
        # TODO: Fix static sizes to be fetched from ir.config_parameter
        values = {
            "channel": channel,
            "maxsize": 20,
            "maxwidth": 1080,
            "maxheight": 1080,
        }
        return request.render(
            "website_channel_messages.channel",
            values
        )

    @http.route(
        ["/website_channel/<int:channel_id>/message"],
        type="http",
        auth="user",
        website=True,
        methods=["POST"]
    )
    def channel_send_message(self, channel_id=None, **post):
        """
        Message submission handler for channel

        :param channel_id: related channel ID
        :param post: submitted form payload
        """
        user = request.env.user
        channel = request.env["mail.channel"].sudo().search([
            ("id", "=", channel_id),
            ("channel_partner_ids", "in", [user.partner_id.id]),
        ], limit=1)
        if not channel:
            return request.render("website.404")

        redirect_url = post.get("redirect_url")
        process_message(user, channel, post)

        return request.redirect(redirect_url)

    @http.route(
        ["/website_channel/update_messages"],
        type="json",
        auth="user",
    )
    def channel_update_messages(self, channel_id, timestamp, csrf_token):
        """
        Update messages for channel.

        :param channel_id: channel ID
        :param timestamp: timestamp of previous update
        :return: new messages rendered HTML
        """
        channel = request.env["mail.channel"].sudo().search([
            ('id', '=', channel_id)
        ], limit=1)
        messages_html = ""
        if channel:
            timestamp = str(timestamp).split('.')[0]
            timestamp_date = str(datetime.fromtimestamp(int(timestamp)))
            new_messages = request.env['mail.message'].search([
                ('model', '=', 'mail.channel'),
                ('res_id', '=', channel.id),
                ('date', '>', timestamp_date)
            ])
            if new_messages:
                for message in new_messages:
                    render_values = {
                        "message": message
                    }
                    messages_html += request.env["ir.ui.view"].render_template(
                        "website_channel_messages.single_message",
                        render_values,
                    ).decode('UTF-8')
        return messages_html

    @http.route([
        "/website_channel/create",
    ], type="json", auth="user")
    def channel_create(self, recipients, csrf_token):
        """
        Create new channel if no chat exists for the selected recipients.

        :param recipients: partner IDs
        :return: JSON
        """
        current_user = request.env.user
        MailChannel = request.env["mail.channel"]
        values = {}
        recipients.append(current_user.partner_id.id)
        recipients.sort()

        channel = MailChannel.sudo().search([
            ("channel_type", "=", "chat"),
            ("channel_partner_ids", "in", recipients),
        ]).filtered(lambda r: sorted(r.channel_partner_ids.ids) == recipients)

        if channel:
            values["id"] = channel.id
        else:
            values["id"] = MailChannel.sudo().create({
                'channel_partner_ids': [(4, partner_id) for partner_id in recipients],
                'public': 'private',
                'channel_type': 'chat',
                'email_send': False,
                'name': ', '.join(request.env['res.partner'].sudo()
                                  .browse(recipients).mapped('name')),
            }).id
        return values
