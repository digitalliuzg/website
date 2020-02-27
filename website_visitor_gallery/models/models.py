from odoo import api
from odoo import fields
from odoo import models


class VisitorImageCategory(models.Model):
    _name = "vimage.category"
    name = fields.Char(string="Name")


class WebsiteVisitorImage(models.Model):
    _name = "visitor.image"
    _description = "Image uploaded by website visitor"

    name = fields.Char(string="Name")
    category = fields.Many2one(
        string="Category", comodel_name="vimage.category", ondelete="restrict"
    )
    website_published = fields.Boolean(string="Published on website", default=False)
    active = fields.Boolean(default=True)
    image_url = fields.Char(string="Image URL")
    filename = fields.Char(string="Filename")
    attachment = fields.Many2one(
        string="Attachment Image", comodel_name="ir.attachment", ondelete="cascade"
    )
    attachment_image = fields.Binary(related="attachment.datas")

    def get_category_list(self):
        categories = []
        for category in self.env["vimage.category"].search([]):
            categories.append(category.name)
        return categories

    def get_image_urls_by_category(self):
        ret = []
        for category in self.env["vimage.category"].search([]):
            image_urls = [category.name]
            for image in self.search(
                [("category.id", "=", category.id), ("website_published", "=", True)]
            ):
                image_urls.append(image.image_url)
            ret.append(image_urls)
        return ret

    @api.model
    def get_published_urls(self):
        image_urls = []
        for image in self.search([("website_published", "=", True)]):
            image_urls.append(image.image_url)
        return image_urls

    def toggle_website_published(self):
        self.website_published = not self.website_published

    @api.model
    def create(self, vals):
        super(WebsiteVisitorImage, self).create(vals)

    def unlink(selfs):
        for self in selfs:
            self.attachment.unlink()
            super(WebsiteVisitorImage, self).unlink()
