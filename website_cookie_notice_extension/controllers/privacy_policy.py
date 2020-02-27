# 1. Standard library imports:
# 2. Known third party imports:
# 3. Odoo imports (openerp):
from odoo import http
from odoo.http import request

# 4. Imports from Odoo modules:


class PrivacyPolicy(http.Controller):
    @http.route("/privacy-policy", type="http", website=True, auth="public")
    def page_certificate_verification(self, **kw):
        return request.render("website_cookie_notice_extension.privacy_policy")
