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

import os
from PIL import Image
from io import BytesIO
import logging
import base64

from odoo.http import request
from odoo.tools import image_save_for_web

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

    :param image: Image data in binary
    :return: Compressed and resized image data in binary
    """
    max_width_key = 'website_file_process.image_max_width'
    max_height_key = 'website_file_process.image_max_height'
    MAX_WIDTH = int(request.env['ir.config_parameter'].sudo().get_param(
        max_width_key))
    MAX_HEIGHT = int(request.env['ir.config_parameter'].sudo().get_param(
        max_height_key))
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

    :param file: processed file
    :return: boolean if the file was too big
    """
    max_size_key = 'website_file_process.attachment_max_size'
    MAX_SIZE = int(request.env['ir.config_parameter'].sudo().get_param(
        max_size_key))
    too_big = False
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)
    if file_size > MAX_SIZE * 1024 * 1024:
        too_big = True
        _logger.warning("Attachment filesize too big: %d MB" % (
            file_size / 1024 / 1024))
    return too_big


def process_message(self, user, record, data):
    """
    Process message posted to student record:
    - Compress and resize image
    - Check that the attachment isn't too big
    - Notify related partners (teachers, student)
    :param user: current user
    :param record: student record this competence is related to
    :param data: submitted form data
    """
    comment = data.get('comment')
    image = data.get('resized') or data.get('image')
    file = data.get('file')
    attachment_list = list()
    error = False
    if comment:
        if image:
            # Transparent PNG's have black background, but this shouldn't
            # be a big issue
            if data.get('resized'):
                img_string = data.get('resized').split(",")[1]
                image_data = base64.b64decode(img_string)
            else:
                image_data = image.read()
            resized = compress_image(image_data)
            mimetype = data.get('image').mimetype
            filename = data.get(
                'image').filename if 'png' not in mimetype else 'image.jpg'
            attachment_list.append((filename, resized))
        if file:
            too_big = process_file(file)
            if too_big:
                error = True
    return error
