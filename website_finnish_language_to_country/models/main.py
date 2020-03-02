
from odoo import http
from odoo.http import request
from odoo.addons.website.controllers.main import Website


class Extension(Website):

    @http.route()
    def change_lang(self, lang, r='/', **kwargs):

        if lang == 'default':
            lang = request.website.default_lang_code
            r = '/%s%s' % (lang, r or '/')

        users = request.env['res.users'].sudo().search([])

        guest_users = [
            request.env.ref(
                'base.default_user_res_partner'
            ).id,
            request.env.ref(
                'base.public_partner'
            ).id
        ]

        if lang == request.env.ref('base.lang_fi').code:
            for user in users:
                if (user.id == request.env.uid and
                        request.env.uid not in guest_users and
                        not user.country_id.id):
                    user.country_id = request.env.ref('base.fi')

        return super(Extension, self).change_lang(lang, r)
