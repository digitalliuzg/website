from odoo.addons.portal.controllers.portal import CustomerPortal
from odoo.addons.website_sale.controllers.main import WebsiteSale
from odoo.http import request, route


class AccountCountries(CustomerPortal):
    @route(["/my/account"], type="http", auth="user", website=True)
    def account(self, redirect=None, **post):
        res = super(AccountCountries, self).account(redirect=None, **post)
        europe = request.env.ref("base.europe").country_ids
        res.qcontext["countries"] = europe
        return res


class WebsiteSale(WebsiteSale):
    @route(
        ["/shop/address"],
        type="http",
        methods=["GET", "POST"],
        auth="public",
        website=True,
        sitemap=False,
    )
    def address(self, **kw):
        res = super(WebsiteSale, self).address(**kw)
        europe = request.env.ref("base.europe").country_ids
        res.qcontext["countries"] = europe
        return res
