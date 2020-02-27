##############################################################################
#
#    Author: Tawasta
#    Copyright 2017 Oy Tawasta OS Technologies Ltd. (https://tawasta.fi)
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

{
    "name": "Website Cookie Notice Extension",
    "summary": "Cookie notice disclaimer on website",
    "version": "12.0.1.0.0",
    "category": "Website",
    "website": "https://github.com/Tawasta/website",
    "author": "Tawasta",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ["website_legal_page", "website_cookie_notice"],
    "data": [
        "views/website.xml",
        "views/privacy_policy_template.xml",
        "data/website_cookie_data.xml",
    ],
}
