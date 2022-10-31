from odoo import models, fields, api


class StockMoveBatch(models.Model):
    _name = 'stock.move.batch'
    _description = 'Move Batch'

    product_id = fields.Many2one('product.product', 'Product', required=True)
    uom_id = fields.Many2one('uom.uom', 'Unit of Measure', required=True)
    net_quantity = fields.Float('A consommer', compute='get_net_data', store=True)
    move_raw_ids = fields.One2many('stock.move', compute='get_move_raw_ids')
    product_uom_qty = fields.Float('Qté réelle')
    package_id = fields.Many2one('stock.quant.package', string='Colis source', readonly=True)
    result_package_id = fields.Many2one('stock.quant.package', string='Colis destination', readonly=True)
    scrap_qty = fields.Float('Losses', compute='get_scrap_percentage', store=True)
    scrap_percentage = fields.Float('Losses (%)', group_operator='avg', compute='get_scrap_percentage', store=True)
    reserved_availability = fields.Float('Réservé', compute='get_production_data')
    quantity_done = fields.Float('Consommé', compute='get_quantity_done', inverse='set_quantity_done')
    mrp_production_batch_id = fields.Many2one('mrp.production.batch', ondelete='cascade')
    user_id = fields.Many2one('res.users', related='mrp_production_batch_id.user_id', store=True)
    # routing_id = fields.Many2one('mrp.routing', related='mrp_production_batch_id.routing_id', store=True)
    state = fields.Selection(related='mrp_production_batch_id.state', store=True)

    def write(self, vals):
        if vals.get('product_id'):
            self.move_raw_ids.write({'product_id': vals['product_id']})
        return super().write(vals)

    def action_update_move_raw_data(self, final=False):
        for rec in self.filtered(lambda mb: mb.move_raw_ids):
            factor = rec.product_uom_qty / sum(rec.move_raw_ids.mapped('product_uom_qty')) if sum(rec.move_raw_ids.mapped('product_uom_qty')) else 0
            for move in rec.move_raw_ids:
                if len(move.move_line_ids) > 1:
                    for ml in move.move_line_ids:
                        ml.write({'qty_done': ml.product_uom_qty * factor} if final else {
                            'product_uom_qty': ml.product_uom_qty * factor})
                else:
                    move.write({'quantity_done': move.product_uom_qty * factor} if final else {
                        'product_uom_qty': move.product_uom_qty * factor})
        for rec in self.filtered(lambda mb: not mb.move_raw_ids):
            return

    @api.depends('product_id', 'mrp_production_batch_id.production_ids')
    def get_move_raw_ids(self):
        for rec in self:
            rec.move_raw_ids = rec.mrp_production_batch_id.production_ids.mapped('move_raw_ids').filtered(
                lambda m: m.product_id == rec.product_id)

    @api.depends('product_id')
    def get_net_data(self):
        for rec in self:
            if rec.move_raw_ids:
                rec.net_quantity = sum(rec.move_raw_ids.mapped('product_uom_qty'))

    @api.depends('product_id', 'uom_id', 'mrp_production_batch_id')
    def get_production_data(self):
        for rec in self:
            if rec.move_raw_ids:
                rec.reserved_availability = sum(rec.move_raw_ids.mapped('product_uom_qty'))
            else:
                rec.reserved_availability = 0

    @api.depends('move_raw_ids.quantity_done')
    def get_quantity_done(self):
        for rec in self:
            if rec.move_raw_ids:
                rec.quantity_done = sum(rec.move_raw_ids.mapped('quantity_done'))
            else:
                rec.quantity_done = 0

    def set_quantity_done(self):
        for rec in self:
            factor = rec.quantity_done / sum(rec.move_raw_ids.mapped('product_uom_qty')) if sum(rec.move_raw_ids.mapped('product_uom_qty')) else 0
            for move in rec.move_raw_ids:
                for move in rec.move_raw_ids:
                    if len(move.move_line_ids) > 0:
                        for ml in move.move_line_ids:
                            ml.write({'qty_done': ml.reserved_uom_qty * factor})
                else:
                    move.write({'quantity_done': move.reserved_availability * factor})

    @api.depends('net_quantity', 'product_uom_qty')
    def get_scrap_percentage(self):
        for rec in self.filtered(lambda b: b.net_quantity and b.product_uom_qty):
            rec.scrap_percentage = 100 * (rec.product_uom_qty - rec.net_quantity) / rec.net_quantity
            rec.scrap_qty = rec.product_uom_qty - rec.net_quantity
