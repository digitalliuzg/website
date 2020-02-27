
from odoo.http import request, route
from odoo.addons.portal.controllers.portal import CustomerPortal


class AccountCountries(CustomerPortal):

    @route()
    def account(self, redirect=None, **post):
        res = super(AccountCountries, self).account(redirect=None, **post)
        europe = request.env.ref('base.europe').country_ids
        res.qcontext['countries'] = europe
        return res
