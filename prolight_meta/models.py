# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2016-2016 BADEP. All Rights Reserved.
#    Author: Khalid HAZAM <k.hazam@badep.ma>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Affero General Public License as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
##############################################################################
from openerp.osv import fields as oldfields, osv
from openerp import tools
from openerp import fields, models, api
from dateutil.relativedelta import relativedelta
import openerp.addons.decimal_precision as dp
from openerp.tools.float_utils import float_round

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'
    
    quantity_in_stock = fields.Float(string='Quantité en Stock', digits_compute=dp.get_precision('Product UoS'), related='product_id.qty_available', store=True)
    quantity_forecast = fields.Float(string='Quantité prévue', digits_compute=dp.get_precision('Product UoS'), compute='get_forecast_data',store=True)
    date_expected = fields.Date(string="Date prévue", compute='get_forecast_data')
    
    @api.one
    @api.depends('delay','product_id','order_id.date_order')
    def get_forecast_data(self):
        self.date_expected = fields.Datetime.to_string(fields.Datetime.from_string(self.order_id.date_order) + relativedelta(days=self.delay))
        self.quantity_forecast = self.product_id and self.product_id.with_context({'date_expected': self.date_expected}).virtual_available or 0

    @api.multi
    def product_id_change(self, pricelist, product, qty=0,
            uom=False, qty_uos=0, uos=False, name='', partner_id=False,
            lang=False, update_tax=True, date_order=False, packaging=False, fiscal_position=False, flag=False):
        
        product_obj = self.env['product.product'].browse(product)
        result = super(SaleOrderLine, self).product_id_change(pricelist, product, qty, uom, qty_uos, uos, name,
                                        partner_id, lang, update_tax, date_order, packaging,
                                        fiscal_position, flag)
        result['value'].update({'quantity_in_stock': product_obj.qty_available, 'quantity_forecast': self.quantity_forecast})
        return result
        
class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    famille = fields.Many2one('product.template.famille', required=True)
    type2 = fields.Many2one('product.template.type', required=True, string="Type",)
    modele = fields.Many2one('product.template.modele', required=True)
    couleur = fields.Many2one('product.template.couleur', required=True)
    puissance = fields.Many2one('product.template.puissance', required=True)
    caracteristique = fields.Many2one('product.template.caracteristique', required=True)
    no_couleur = fields.Boolean(string="Non défini", default=False)
    no_puissance = fields.Boolean(string="Non défini", default=False)
    no_caracteristique = fields.Boolean(string="Non défini",default=False)
    commentaire = fields.Char()
    articles_similaires = fields.Many2many(comodel_name='product.template',relation='product_template_template_rel',column1='product_template_id1',column2='product_template_id2')
    sale_ok = fields.Boolean(default=False)
    
    @api.model
    def hibernate(self,delay=12):
        products = self.env['stock.move'].search([('date','<',fields.Datetime.to_string(fields.Datetime.from_string(fields.Datetime.now()) - relativedelta(months=delay)))]).mapped('product_id.product_tmpl_id')
        products.write({'active': False})
        return True
    
    @api.onchange('famille')
    def onchange_famille(self):
        self.type2=False
        return {
            'domain': {
                'type2': [('id', 'in', self.famille.types.ids )],
            },
        }

    @api.onchange('type2')
    def onchange_type2(self):
        self.modele=False

    @api.onchange('modele')
    def onchange_modele(self):
        self.couleur=False
        self.puissance=False
        self.caracteristique=False
    
    @api.onchange('no_couleur')
    def onchange_no_couleur(self):
        self.couleur=False

    @api.onchange('no_puissance')
    def onchange_no_puissance(self):
        self.puissance=False

    @api.onchange('no_caracteristique')
    def onchange_no_caracteristique(self):
        self.caracteristique=False

    @api.onchange('active','sale_ok')
    def onchange_activation(self):
        self.famille = False
        
    @api.onchange('famille','type','modele','couleur','puissance','caracteristique','commentaire')
    def generate_name(self):
        name = ''
        if self.active and self.sale_ok and self.type == 'product':
            name = (self.famille.name if self.famille else '') + (' - ' + self.type2.name if self.type2 else '') + (' - ' + self.modele.name if self.modele else '') + (' - ' + self.couleur.name if self.couleur else '') + (' - ' + self.puissance.name if self.puissance else '') + (' - ' + self.caracteristique.name if self.caracteristique else '') + (' - ' + self.commentaire if self.commentaire else '')
            self.name = name
    
class ProductTemplateFamille(models.Model):
    _name = 'product.template.famille'
    name = fields.Char(required=True, string='Nom')
    types = fields.Many2many('product.template.type', 'product_famille_type_rel')
    
class ProductTemplateType(models.Model):
    _name = 'product.template.type'
    name = fields.Char(required=True, string='Nom')
    familles = fields.Many2many('product.template.famille', 'product_famille_type_rel')
    has_couleur = fields.Boolean(string='Avec Couleurs',default=True)
    has_puissance = fields.Boolean(string='Avec Puissance',default=True)
    has_caracteristique = fields.Boolean(string='Avec Caractéristiques',default=True)
    
class ProductTemplateModele(models.Model):
    _name = 'product.template.modele'
    name = fields.Char(required=True, string='Nom')
    types = fields.Many2many('product.template.type', 'product_type_modele_rel')
    
class ProductTemplateCouleur(models.Model):
    _name = 'product.template.couleur'
    name = fields.Char(required=True, string='Nom')
    
class ProductTemplatePuissance(models.Model):
    _name = 'product.template.puissance'
    name = fields.Char(required=True, string='Nom')
    
class ProductTemplateCaracteristique(models.Model):
    _name = 'product.template.caracteristique'
    name = fields.Char(required=True, string='Nom')
    
class ProductProduct(osv.osv):
    _inherit = 'product.product'
        
    def _product_available(self, cr, uid, ids, field_names=None, arg=False, context=None):
        context = context or {}
        field_names = field_names or []
        domain_products = [('product_id', 'in', ids)]
        domain_quant, domain_move_in, domain_move_out = [], [], []
        domain_quant_loc, domain_move_in_loc, domain_move_out_loc = self._get_domain_locations(cr, uid, ids, context=context)
        domain_move_in += self._get_domain_dates(cr, uid, ids, context=context) + [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_products
        domain_move_out += self._get_domain_dates(cr, uid, ids, context=context) + [('state', 'not in', ('done', 'cancel', 'draft'))] + domain_products
        domain_quant += domain_products

        if context.get('date_expected'):
            domain_move_in.append(('date_expected', '<=', context['date_expected']))
            domain_move_out.append(('date_expected', '<=', context['date_expected']))
        
        if context.get('lot_id'):
            domain_quant.append(('lot_id', '=', context['lot_id']))
        if context.get('owner_id'):
            domain_quant.append(('owner_id', '=', context['owner_id']))
            owner_domain = ('restrict_partner_id', '=', context['owner_id'])
            domain_move_in.append(owner_domain)
            domain_move_out.append(owner_domain)
        if context.get('package_id'):
            domain_quant.append(('package_id', '=', context['package_id']))

        domain_move_in += domain_move_in_loc
        domain_move_out += domain_move_out_loc
        moves_in = self.pool.get('stock.move').read_group(cr, uid, domain_move_in, ['product_id', 'product_qty'], ['product_id'], context=context)
        moves_out = self.pool.get('stock.move').read_group(cr, uid, domain_move_out, ['product_id', 'product_qty'], ['product_id'], context=context)

        domain_quant += domain_quant_loc
        quants = self.pool.get('stock.quant').read_group(cr, uid, domain_quant, ['product_id', 'qty'], ['product_id'], context=context)
        quants = dict(map(lambda x: (x['product_id'][0], x['qty']), quants))

        moves_in = dict(map(lambda x: (x['product_id'][0], x['product_qty']), moves_in))
        moves_out = dict(map(lambda x: (x['product_id'][0], x['product_qty']), moves_out))
        res = {}
        for product in self.browse(cr, uid, ids, context=context):
            id = product.id
            qty_available = float_round(quants.get(id, 0.0), precision_rounding=product.uom_id.rounding)
            incoming_qty = float_round(moves_in.get(id, 0.0), precision_rounding=product.uom_id.rounding)
            outgoing_qty = float_round(moves_out.get(id, 0.0), precision_rounding=product.uom_id.rounding)
            virtual_available = float_round(quants.get(id, 0.0) + moves_in.get(id, 0.0) - moves_out.get(id, 0.0), precision_rounding=product.uom_id.rounding)
            res[id] = {
                'qty_available': qty_available,
                'incoming_qty': incoming_qty,
                'outgoing_qty': outgoing_qty,
                'virtual_available': virtual_available,
            }
        return res

    _columns = {
        'qty_available': oldfields.function(_product_available, multi='qty_available',
            type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Quantity On Hand',
            fnct_search=_search_product_quantity,
            help="Current quantity of products.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored at this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                 "stored in the Stock Location of the Warehouse of this Shop, "
                 "or any of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "with 'internal' type."),
        'virtual_available': oldfields.function(_product_available, multi='qty_available',
            type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Forecast Quantity',
            fnct_search=_search_product_quantity,
            help="Forecast quantity (computed as Quantity On Hand "
                 "- Outgoing + Incoming)\n"
                 "In a context with a single Stock Location, this includes "
                 "goods stored in this location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods stored in the Stock Location of this Warehouse, or any "
                 "of its children.\n"
                 "Otherwise, this includes goods stored in any Stock Location "
                 "with 'internal' type."),
        'incoming_qty': oldfields.function(_product_available, multi='qty_available',
            type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Incoming',
            fnct_search=_search_product_quantity,
            help="Quantity of products that are planned to arrive.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods arriving to this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods arriving to the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "Otherwise, this includes goods arriving to any Stock "
                 "Location with 'internal' type."),
        'outgoing_qty': oldfields.function(_product_available, multi='qty_available',
            type='float', digits_compute=dp.get_precision('Product Unit of Measure'),
            string='Outgoing',
            fnct_search=_search_product_quantity,
            help="Quantity of products that are planned to leave.\n"
                 "In a context with a single Stock Location, this includes "
                 "goods leaving this Location, or any of its children.\n"
                 "In a context with a single Warehouse, this includes "
                 "goods leaving the Stock Location of this Warehouse, or "
                 "any of its children.\n"
                 "Otherwise, this includes goods leaving any Stock "
                 "Location with 'internal' type.")
                }
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
