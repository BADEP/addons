from odoo import models

# TODO: This is a dirty hack which renders all image_small of res_partner public! It's needed for the icon of the push notification.
# TODO: Maybe in the future add an access_token or verify if the request comes from FCM
class Http(models.AbstractModel):
    _inherit = 'ir.http'
    def binary_content(self, xmlid=None, model='ir.attachment', id=None, field='datas',
                       unique=False, filename=None, filename_field='name', download=False,
                       mimetype=None, default_mimetype='application/octet-stream',
                       access_token=None):
        return super(Http, self.sudo() if model == 'res.partner' and field == 'image_small' else self).binary_content(
            xmlid=xmlid, model=model, id=id, field=field, unique=unique, filename=filename,
            filename_field=filename_field, download=download, mimetype=mimetype,
            default_mimetype=default_mimetype, access_token=access_token)
