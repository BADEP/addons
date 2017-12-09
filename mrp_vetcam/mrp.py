# -*- coding: utf-8 -*-
##############################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (c) 2010-2013 Elico Corp. All Rights Reserved.
#    Author: Yannick Gouin <yannick.gouin@elico-corp.com>
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
from openerp import models, fields, api
import openerp.addons.decimal_precision as dp
from collections import OrderedDict
from openerp.osv import osv
from openerp.tools import float_compare, float_is_zero
from openerp.addons.product import _common
from openerp import tools, SUPERUSER_ID
from openerp.tools.translate import _

class mrp_production(models.Model):
    _inherit = 'mrp.production'
    
    @api.cr_uid_id_context
    def action_produce(self, cr, uid, production_id, production_qty, production_mode, wiz=False, context=None):
        """ To produce final product based on production mode (consume/consume&produce).
        If Production mode is consume, all stock move lines of raw materials will be done/consumed.
        If Production mode is consume & produce, all stock move lines of raw materials will be done/consumed
        and stock move lines of final product will be also done/produced.
        @param production_id: the ID of mrp.production object
        @param production_qty: specify qty to produce in the uom of the production order
        @param production_mode: specify production mode (consume/consume&produce).
        @param wiz: the mrp produce product wizard, which will tell the amount of consumed products needed
        @return: True
        """
        stock_mov_obj = self.pool.get('stock.move')
        uom_obj = self.pool.get("product.uom")
        production = self.browse(cr, uid, production_id, context=context)
        production_qty_uom = uom_obj._compute_qty(cr, uid, production.product_uom.id, production_qty, production.product_id.uom_id.id)
        precision = self.pool['decimal.precision'].precision_get(cr, uid, 'Product Unit of Measure')

        main_production_move = False
        if production_mode == 'consume_produce':
            # To produce remaining qty of final product
            produced_products = {}
            for produced_product in production.move_created_ids2:
                if produced_product.scrapped:
                    continue
                if not produced_products.get(produced_product.product_id.id, False):
                    produced_products[produced_product.product_id.id] = 0
                produced_products[produced_product.product_id.id] += produced_product.product_qty
            for produce_product in production.move_created_ids:
                subproduct_factor = self._get_subproduct_factor(cr, uid, production.id, produce_product.id, context=context)
                lot_id = False
                if wiz:
                    lot_id = wiz.lot_id.id
                qty = min(subproduct_factor * production_qty_uom, produce_product.product_qty) #Needed when producing more than maximum quantity
                new_moves = stock_mov_obj.action_consume(cr, uid, [produce_product.id], qty,
                                                         location_id=produce_product.location_id.id, restrict_lot_id=lot_id, context=context)
                stock_mov_obj.write(cr, uid, new_moves, {'production_id': production_id}, context=context)
                remaining_qty = subproduct_factor * production_qty_uom - qty
                if not float_is_zero(remaining_qty, precision_digits=precision):
                    # In case you need to make more than planned
                    #consumed more in wizard than previously planned
                    extra_move_id = stock_mov_obj.copy(cr, uid, produce_product.id, default={'product_uom_qty': remaining_qty,
                                                                                             'production_id': production_id}, context=context)
                    stock_mov_obj.action_confirm(cr, uid, [extra_move_id], context=context)
                    stock_mov_obj.action_done(cr, uid, [extra_move_id], context=context)

                if produce_product.product_id.id == production.product_id.id:
                    main_production_move = produce_product.id

        if production_mode in ['consume', 'consume_produce']:
            if wiz:
                consume_lines = []
                for cons in wiz.consume_lines:
                    consume_lines.append({'bom_line': cons.bom_line.id, 'product_id': cons.product_id.id, 'lot_id': cons.lot_id.id, 'product_qty': cons.product_qty})
            else:
                consume_lines = self._calculate_qty(cr, uid, production, production_qty_uom, context=context)
            for consume in consume_lines:
                remaining_qty = consume['product_qty']
                for raw_material_line in production.move_lines:
                    if raw_material_line.state in ('done', 'cancel'):
                        continue
                    if remaining_qty <= 0:
                        break
                    if consume['bom_line'] != raw_material_line.bom_line.id:
                        continue
                    consumed_qty = min(remaining_qty, raw_material_line.product_qty)
                    stock_mov_obj.action_consume(cr, uid, [raw_material_line.id], consumed_qty, raw_material_line.location_id.id,
                                                 restrict_lot_id=consume['lot_id'], consumed_for=main_production_move, context=context)
                    remaining_qty -= consumed_qty
                if not float_is_zero(remaining_qty, precision_digits=precision):
                    #consumed more in wizard than previously planned
                    product = self.pool.get('product.product').browse(cr, uid, consume['product_id'], context=context)
                    extra_move_id = self._make_consume_line_from_data(cr, uid, production, product, product.uom_id.id, remaining_qty, False, 0, context=context)
                    stock_mov_obj.write(cr, uid, [extra_move_id], {'restrict_lot_id': consume['lot_id'],
                                                                    'consumed_for': main_production_move}, context=context)
                    stock_mov_obj.action_done(cr, uid, [extra_move_id], context=context)

        self.message_post(cr, uid, production_id, body=_("%s produced") % self._description, context=context)

        # Remove remaining products to consume if no more products to produce
        if not production.move_created_ids and production.move_lines:
            stock_mov_obj.action_cancel(cr, uid, [x.id for x in production.move_lines], context=context)

        self.signal_workflow(cr, uid, [production_id], 'button_produce_done')
        return True
    
    @api.model
    def _make_production_consume_line(self, line):
        res = super(mrp_production, self)._make_production_consume_line(line)
        self.env['stock.move'].browse(res).bom_line = line.bom_line
        return res
        
    @api.cr_uid_context
    def _get_consumed_data(self, cr, uid, production, context=None):
        ''' returns a dictionary containing for each raw material of the given production, its quantity already consumed (in the raw material UoM)
        '''
        consumed_data = {}
        # Calculate already consumed qtys
        for consumed in production.move_lines2:
            if consumed.scrapped:
                continue
            if not consumed_data.get(consumed.bom_line.id, False):
                consumed_data[consumed.bom_line.id] = 0
            consumed_data[consumed.bom_line.id] += consumed.product_qty
        return consumed_data

    @api.cr_uid_context
    def _calculate_qty(self, cr, uid, production, product_qty=0.0, context=None):

        """
            Calculates the quantity still needed to produce an extra number of products
            product_qty is in the uom of the product
        """
        quant_obj = self.pool.get("stock.quant")
        uom_obj = self.pool.get("product.uom")
        produced_qty = self._get_produced_qty(cr, uid, production, context=context)
        consumed_data = self._get_consumed_data(cr, uid, production, context=context)

        #In case no product_qty is given, take the remaining qty to produce for the given production
        if not product_qty:
            product_qty = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, production.product_id.uom_id.id) - produced_qty
        production_qty = uom_obj._compute_qty(cr, uid, production.product_uom.id, production.product_qty, production.product_id.uom_id.id)

        scheduled_qty = OrderedDict()
        dosing = OrderedDict()
        for scheduled in production.product_lines:
            if scheduled.product_id.type == 'service':
                continue
            qty = uom_obj._compute_qty(cr, uid, scheduled.product_uom.id, scheduled.product_qty, scheduled.product_id.uom_id.id)
            if scheduled_qty.get(scheduled.bom_line.id):
                scheduled_qty[scheduled.bom_line.id] += qty
                dosing[scheduled.bom_line.id] += scheduled.dosing
            else:
                scheduled_qty[scheduled.bom_line.id] = qty
                dosing[scheduled.bom_line.id] = scheduled.dosing
        dicts = OrderedDict()
        # Find product qty to be consumed and consume it
        for bom_line in scheduled_qty.keys():

            consumed_qty = consumed_data.get(bom_line, 0.0)
            
            # qty available for consume and produce
            sched_product_qty = scheduled_qty[bom_line]
            qty_avail = sched_product_qty - consumed_qty
            if qty_avail <= 0.0:
                # there will be nothing to consume for this raw material
                continue

            if not dicts.get(bom_line):
                dicts[bom_line] = {}

            # total qty of consumed product we need after this consumption
            if product_qty + produced_qty <= production_qty:
                total_consume = ((product_qty + produced_qty) * sched_product_qty / production_qty)
            else:
                total_consume = sched_product_qty
            qty = total_consume - consumed_qty

            # Search for quants related to this related move
            for move in production.move_lines:
                if qty <= 0.0:
                    break
                if move.bom_line.id != bom_line:
                    continue

                q = min(move.product_qty, qty)
                quants = quant_obj.quants_get_prefered_domain(cr, uid, move.location_id, move.product_id, q, domain=[('qty', '>', 0.0)],
                                                     prefered_domain_list=[[('reservation_id', '=', move.id)]], context=context)
                for quant, quant_qty in quants:
                    if quant:
                        lot_id = quant.lot_id.id
                        if not bom_line in dicts.keys():
                            dicts[bom_line] = {lot_id: quant_qty}
                        elif lot_id in dicts[bom_line].keys():
                            dicts[bom_line][lot_id] += quant_qty
                        else:
                            dicts[bom_line][lot_id] = quant_qty
                        qty -= quant_qty
            if float_compare(qty, 0, self.pool['decimal.precision'].precision_get(cr, uid, 'Product Unit of Measure')) == 1:
                if dicts[bom_line].get(False):
                    dicts[bom_line][False] += qty
                else:
                    dicts[bom_line][False] = qty

        consume_lines = []
        for bom_line in dicts.keys():
            bom_line_obj = self.pool.get('mrp.bom.line').browse(cr, uid, bom_line, context=context)
            for lot, qty in dicts[bom_line].items():
                consume_lines.append({'bom_line': bom_line, 'product_id': bom_line_obj.product_id.id, 'product_ideal_qty': qty, 'product_qty': qty, 'lot_id': lot, 'dosing': dosing[bom_line]})
        return consume_lines

class mrp_bom(models.Model):
    _inherit = 'mrp.bom'
    
    @api.cr_uid_context
    def _bom_explode(self, cr, uid, bom, product, factor, properties=None, level=0, routing_id=False, previous_products=None, master_bom=None, context=None):
        """ Finds Products and Work Centers for related BoM for manufacturing order.
        @param bom: BoM of particular product template.
        @param product: Select a particular variant of the BoM. If False use BoM without variants.
        @param factor: Factor represents the quantity, but in UoM of the BoM, taking into account the numbers produced by the BoM
        @param properties: A List of properties Ids.
        @param level: Depth level to find BoM lines starts from 10.
        @param previous_products: List of product previously use by bom explore to avoid recursion
        @param master_bom: When recursion, used to display the name of the master bom
        @return: result: List of dictionaries containing product details.
                 result2: List of dictionaries containing Work Center details.
        """
        uom_obj = self.pool.get("product.uom")
        routing_obj = self.pool.get('mrp.routing')
        master_bom = master_bom or bom


        def _factor(factor, product_efficiency, product_rounding):
            factor = factor / (product_efficiency or 1.0)
            factor = _common.ceiling(factor, product_rounding)
            if factor < product_rounding:
                factor = product_rounding
            return factor

        factor = _factor(factor, bom.product_efficiency, bom.product_rounding)

        result = []
        result2 = []

        routing = (routing_id and routing_obj.browse(cr, uid, routing_id)) or bom.routing_id or False
        if routing:
            for wc_use in routing.workcenter_lines:
                wc = wc_use.workcenter_id
                d, m = divmod(factor, wc_use.workcenter_id.capacity_per_cycle)
                mult = (d + (m and 1.0 or 0.0))
                cycle = mult * wc_use.cycle_nbr
                result2.append({
                    'name': tools.ustr(wc_use.name) + ' - ' + tools.ustr(bom.product_tmpl_id.name_get()[0][1]),
                    'workcenter_id': wc.id,
                    'sequence': level + (wc_use.sequence or 0),
                    'cycle': cycle,
                    'hour': float(wc_use.hour_nbr * mult + ((wc.time_start or 0.0) + (wc.time_stop or 0.0) + cycle * (wc.time_cycle or 0.0)) * (wc.time_efficiency or 1.0)),
                })

        for bom_line_id in bom.bom_line_ids:
            if self._skip_bom_line(cr, uid, bom_line_id, product, context=context):
                continue
            if set(map(int, bom_line_id.property_ids or [])) - set(properties or []):
                continue

            if previous_products and bom_line_id.product_id.product_tmpl_id.id in previous_products:
                raise osv.except_osv(_('Invalid Action!'), _('BoM "%s" contains a BoM line with a product recursion: "%s".') % (master_bom.name,bom_line_id.product_id.name_get()[0][1]))

            quantity = _factor(bom_line_id.product_qty * factor, bom_line_id.product_efficiency, bom_line_id.product_rounding)
            bom_id = self._bom_find(cr, uid, product_id=bom_line_id.product_id.id, properties=properties, context=context)

            #If BoM should not behave like PhantoM, just add the product, otherwise explode further
            if bom_line_id.type != "phantom" and (not bom_id or self.browse(cr, uid, bom_id, context=context).type != "phantom"):
                result.append({
                    'name': bom_line_id.product_id.name,
                    'product_id': bom_line_id.product_id.id,
                    'product_qty': quantity,
                    'bom_line': bom_line_id.id,
                    'dosing': bom_line_id.dosing,
                    'prev_dosing': bom_line_id.dosing,
                    'product_uom': bom_line_id.product_uom.id,
                    'product_uos_qty': bom_line_id.product_uos and _factor(bom_line_id.product_uos_qty * factor, bom_line_id.product_efficiency, bom_line_id.product_rounding) or False,
                    'product_uos': bom_line_id.product_uos and bom_line_id.product_uos.id or False,
                })
            elif bom_id:
                all_prod = [bom.product_tmpl_id.id] + (previous_products or [])
                bom2 = self.browse(cr, uid, bom_id, context=context)
                # We need to convert to units/UoM of chosen BoM
                factor2 = uom_obj._compute_qty(cr, uid, bom_line_id.product_uom.id, quantity, bom2.product_uom.id)
                quantity2 = factor2 / bom2.product_qty
                res = self._bom_explode(cr, uid, bom2, bom_line_id.product_id, quantity2,
                    properties=properties, level=level + 10, previous_products=all_prod, master_bom=master_bom, context=context)
                result = result + res[0]
                result2 = result2 + res[1]
            else:
                raise osv.except_osv(_('Invalid Action!'), _('BoM "%s" contains a phantom BoM line but the product "%s" does not have any BoM defined.') % (master_bom.name,bom_line_id.product_id.name_get()[0][1]))

        return result, result2

class mrp_bom_line(models.Model):
    _inherit = 'mrp.bom.line'
    
    dosing = fields.Float(string='Dosage', digits_compute=dp.get_precision('Product UoS'))

class mrp_production_product_line(models.Model):
    _inherit = 'mrp.production.product.line'
    
    dosing = fields.Float(string='Dosage', digits_compute=dp.get_precision('Product UoS'))
    prev_dosing = fields.Float(string='Dosage', digits_compute=dp.get_precision('Product UoS'))
    bom_line = fields.Many2one('mrp.bom.line')

    @api.one
    @api.onchange('dosing')
    def onchange_dosing(self):
        if self.prev_dosing != 0:
            self.product_qty = self.product_qty * self.dosing/self.prev_dosing
            self.prev_dosing = self.dosing

class mrp_product_produce_line(models.TransientModel):
    _inherit = "mrp.product.produce.line"
    
    product_ideal_qty = fields.Float(digits_compute=dp.get_precision('Product Unit of Measure'),
                                         string='Quantité idéale')
    product_theorical_qty = fields.Float(digits_compute=dp.get_precision('Product Unit of Measure'),
                                     string='Quantité Théorique')
    dosing = fields.Float(string='Dosage', digits_compute=dp.get_precision('Product UoS'))
    batch_qty = fields.Integer(string='Nombre de gâchés')
    efficiency = fields.Float(compute='get_efficiency', string='Efficacité')
    deviation = fields.Float(compute='get_deviation', string='Déviation')
    bom_line = fields.Many2one('mrp.bom.line')

    @api.one
    @api.onchange('batch_qty', 'dosing')
    def set_theorical_qty(self):
        self.product_theorical_qty = self.batch_qty * self.dosing

    @api.one
    @api.onchange('product_theorical_qty')
    def onchange_theorical_qty(self):
        self.batch_qty = round(self.product_theorical_qty/self.dosing)

    @api.one
    @api.depends('product_qty','product_ideal_qty')
    def get_efficiency(self):
        self.efficiency = (self.product_ideal_qty/self.product_qty)*100

    @api.one
    @api.depends('product_qty','product_theorical_qty')
    def get_deviation(self):
        if self.product_theorical_qty != 0:
            self.deviation = 100*(self.product_qty - self.product_theorical_qty)/self.product_theorical_qty
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4:
