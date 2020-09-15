# -*- coding: utf-8 -*-

from odoo import models, fields, api

class ResPartner(models.Model):
    _inherit = 'res.partner'
    
    supplierinfo_ids = fields.One2many('product.supplierinfo', 'name', string='Liste des prix')
    

    def act_show_supplierinfo(self):
        action = self.env.ref('product.product_supplierinfo_type_action')

        result = {
            'name': action.name,
            'help': action.help,
            'type': action.type,
            'view_type': action.view_type,
            'view_mode': action.view_mode,
            'target': action.target,
            'context': action.context,
            'res_model': action.res_model,
        }
        result['domain'] = "[('id','in',["+','.join(map(str, self.supplierinfo_ids.ids))+"])]"
        return result