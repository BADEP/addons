# -*- coding: utf-8 -*-

 
from openerp import models, fields, api


class ProjectOffer(models.Model):
    
    _name = 'project.offer'
    _inherit = ['project.offer','website.seo.metadata']

    website_published = fields.Boolean('Published', copy=False, default=False)
    website_description = fields.Html('Website description', translate=True)
    website_url = fields.Char(compute='_website_url', string="Website URL")

    @api.multi
    def _website_url(self):
        res = dict.fromkeys(self.ids, '')
        for rec in self:
            res[rec.id] = "/offers/detail/%s" % rec.id
        return res

    @api.multi
    def action_open(self):
        self.write({'website_published': True})
        return super(ProjectOffer, self).action_open()
