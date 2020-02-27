import base64
import logging
import mimetypes

import werkzeug
from odoo import http
from odoo.addons.website_slides.controllers.main import WebsiteSlides
from odoo.http import request

_logger = logging.getLogger(__name__)


class WebsiteFilebank(WebsiteSlides):
    @http.route(
        """/slides/slide/<model("slide.slide"):slide>/download""",
        type="http",
        auth="public",
        website=True,
    )
    def slide_download(self, slide, **kw):
        slide = slide.sudo()
        if slide.download_security == "public" or (
            slide.download_security == "user" and
            request.env.user and
            request.env.user != request.website.user_id
        ):
            filecontent = base64.b64decode(slide.datas)
            disposition = "attachment; filename={}.{}".format(
                werkzeug.urls.url_quote(slide.name),
                mimetypes.guess_all_extensions(slide.mime_type)[0].replace(".", ""),
            )
            return request.make_response(
                filecontent,
                [
                    ("Content-Type", slide.mime_type),
                    ("Content-Length", len(filecontent)),
                    ("Content-Disposition", disposition),
                ],
            )
        elif not request.session.uid and slide.download_security == "user":
            return request.redirect("/web/login?redirect=/slides/slide/%s" % (slide.id))
        return request.render("website.403")

    @http.route("/filebank", type="http", auth="public", website=True)
    def filebank_index(self, *args, **post):
        # domain = request.website.website_domain()
        filebank_ids = [
            request.env.ref("website_filebank.filebank_public").id,
            request.env.ref("website_filebank.filebank_partial").id,
        ]
        channels = request.env["slide.channel"].search(
            [("id", "in", filebank_ids)], order="sequence, id"
        )
        if not channels:
            return request.render("website_slides.channel_not_found")
        elif len(channels) == 1:
            return request.redirect("/slides/%s" % channels.id)
        values = {
            "channels": channels,
            "user": request.env.user,
            "is_public_user": request.env.user == request.website.user_id,
        }
        return request.render("website_filebank.filebank_listing", values)

    @http.route("/slides", type="http", auth="public", website=True)
    def slides_index(self, *args, **post):
        """ Returns a list of available channels: if only one is available,
        redirects directly to its slides
        """
        # domain = request.website.website_domain()
        filebank_ids = [
            request.env.ref("website_filebank.filebank_public").id,
            # request.env.ref("website_filebank.filebank_partial").id
        ]
        channels = request.env["slide.channel"].search(
            [("id", "not in", filebank_ids)], order="sequence, id"
        )

        if not channels:
            return request.render("website_slides.channel_not_found")
        elif len(channels) == 1:
            return request.redirect("/slides/%s" % channels.id)
        return request.render(
            "website_slides.channels",
            {
                "channels": channels,
                "user": request.env.user,
                "is_public_user": request.env.user == request.website.user_id,
            },
        )
