from odoo import http, _, tools
import base64
from PIL import Image
from io import BytesIO


class VisitorImgUpload(http.Controller):
    def optimize_img(self, img):
        img = Image.open(BytesIO(img))
        img_optimized = tools.image_save_for_web(img)
        return img_optimized

    @http.route('/visitor_gallery', auth='public', type='http', website=True)
    def visitor_gallery(self, **kw):
        categories = http.request.env['visitor.image'].get_category_list()
        image_urls = http.request.env['visitor.image'].get_published_urls()
        image_urls_by_category = \
            http.request.env['visitor.image'].get_image_urls_by_category()
        return http.request.render('website_visitor_gallery.visitor_gallery', {
            'categories': categories,
            'image_urls': image_urls,
            'image_urls_by_category': image_urls_by_category,
        })

    @http.route(['/visitor_gallery/add_image'], type='http', auth='public',
                methods=['POST'], website=True)
    def create_slide(self, *args, **post):
        if post.get('image'):
            try:
                for img_filestorage in http.request.httprequest.files.getlist('image'):

                    Attachment = http.request.env['ir.attachment'].sudo()
                    VisitorImage = http.request.env['visitor.image'].sudo()

                    img = img_filestorage.read()  # post.get('image').read()
                    img_optimized = self.optimize_img(img)
                    datas = base64.b64encode(img_optimized)
                    filename = img_filestorage.filename
                    category = http.request.env['vimage.category'].search(
                        [('name', '=', post.get('category'))])

                    attachment = Attachment.create({
                        'name': filename,
                        'datas': datas,
                        'type': 'binary',
                        'datas_fname': filename,
                        'public': True,
                    })

                    VisitorImage.create({
                        'name': filename,
                        'filename': filename,
                        'attachment': attachment.id,
                        'image_url': "/web/image/" +
                        str(attachment.id) + "/" + filename,
                        'category': category.id,
                    })

                return http.request.render(
                    'website_visitor_gallery.visitor_gallery_thank_you', {})
            except Exception as e:
                print(e)
                return http.request.render(
                    'website_visitor_gallery.visitor_gallery_error', {
                        'message': ""
                    })

        else:
            return http.request.render(
                'website_visitor_gallery.visitor_gallery_error', {
                    'message': _('Image file missign.')
                })
