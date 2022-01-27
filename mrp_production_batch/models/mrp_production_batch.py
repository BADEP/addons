from odoo import models, fields, api, _
from odoo.exceptions import AccessError

class MrpProductionBatch(models.Model):
    _description = 'Production Batch'
    _name = 'mrp.production.batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.model
    def _get_default_picking_type(self):
        company_id = self.env.context.get('default_company_id', self.env.company.id)
        return self.env['stock.picking.type'].search([
            ('code', '=', 'mrp_operation'),
            ('warehouse_id.company_id', '=', company_id),
        ], limit=1).id

    @api.model
    def _get_default_location_src_id(self):
        location = False
        if self._context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(self.env.context['default_picking_type_id']).default_location_src_id
        if not location:
            location = self.env.ref('stock.stock_location_stock', raise_if_not_found=False)
            try:
                location.check_access_rule('read')
            except (AttributeError, AccessError):
                location = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1).lot_stock_id
        return location and location.id or False

    @api.model
    def _get_default_location_dest_id(self):
        location = False
        if self._context.get('default_picking_type_id'):
            location = self.env['stock.picking.type'].browse(self.env.context['default_picking_type_id']).default_location_dest_id
        if not location:
            location = self.env.ref('stock.stock_location_stock', raise_if_not_found=False)
            try:
                location.check_access_rule('read')
            except (AttributeError, AccessError):
                location = self.env['stock.warehouse'].search([('company_id', '=', self.env.user.company_id.id)], limit=1).lot_stock_id
        return location and location.id or False

    is_locked = fields.Boolean('Is Locked', compute='_compute_is_locked', copy=False)
    reserve_visible = fields.Boolean(
        'Allowed to Reserve Production', compute='_compute_unreserve_visible',
        help='Technical field to check when we can reserve quantities')
    unreserve_visible = fields.Boolean(
        'Allowed to Unreserve Production', compute='_compute_unreserve_visible',
        help='Technical field to check when we can unreserve')
    is_planned = fields.Boolean('Its Operations are Planned', compute='_compute_is_planned', search='_search_is_planned')
    qty_produced = fields.Float(compute="_get_produced_qty", string="Quantity Produced")
    qty_producing = fields.Float(compute="_get_producing_qty", string="Quantity Producing")
    show_lock = fields.Boolean('Show Lock/unlock buttons', compute='_compute_show_lock')
    confirm_cancel = fields.Boolean(compute='_compute_confirm_cancel')
    attribute_value_ids = fields.Many2many('product.template.attribute.value', string='Attributes',
                                           compute='_get_unique_attribute_values')
    name = fields.Char(
        'Reference', copy=False, readonly=True, default=lambda x: _('New'))
    origin = fields.Char(
        'Origin', copy=False,
        help="Reference of the document that generated this production order request.")
    routing_id = fields.Many2one('mrp.routing', 'Routing', store=True)
    # has_moves = fields.Boolean(compute='_has_moves')
    procurement_group_id = fields.Many2one(
        'procurement.group', 'Procurement Group',
        copy=False)
    production_ids = fields.One2many('mrp.production', 'mrp_production_batch_id', copy=True)
    workorder_batch_ids = fields.One2many('mrp.workorder.batch', 'mrp_production_batch_id')
    workorder_batch_done_count = fields.Integer('Batch count', compute='get_workorder_batch_count')
    workorder_batch_count = fields.Integer('Batch count', compute='get_workorder_batch_count')
    move_batch_ids = fields.One2many('stock.move.batch', 'mrp_production_batch_id')
    date_planned_start = fields.Datetime(
        'Scheduled Date Start', copy=False, store=True, compute='_compute_date_planned_start', inverse='_set_date_planned_start',
        index=True, required=False)
    date_planned_finished = fields.Datetime(
        'Scheduled Date Finished', copy=False, default=fields.Datetime.now,
        index=True,
        states={'confirmed': [('readonly', False)]})
    date_start = fields.Datetime('Date Start', compute='get_related_fields')
    date_finished = fields.Datetime('Date Finished', compute='get_related_fields')
    date_deadline = fields.Datetime(
        'Deadline', copy=False, store=True, readonly=True, compute='_compute_date_deadline', inverse='_set_date_deadline',
        help="Informative date allowing to define when the manufacturing order should be processed at the latest to fulfill delivery on time.")
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirmed', 'Confirmed'),
            ('progress', 'In Progress'),
            ('to_close', 'To Close'),
            ('done', 'Done'),
            ('cancel', 'Cancelled')], default='draft', string='State', compute='get_related_fields', store=True,
        track_visibility='onchange')
    user_id = fields.Many2one('res.users', 'Responsible', default=lambda self: self._uid)
    company_id = fields.Many2one('res.company', 'Company',
                                 default=lambda self: self.env['res.company']._company_default_get('mrp.production'),
                                 required=True)
    picking_type_id = fields.Many2one('stock.picking.type', 'Operation Type', required=True,
                                      domain=[('code', '=', 'mrp_operation')],
                                      default=_get_default_picking_type)
    location_src_id = fields.Many2one(
        'stock.location', 'Emplacement de matière première',
        default=_get_default_location_src_id,
        readonly=True,  required=True,
        states={'confirmed': [('readonly', False)]},
        help="Location where the system will look for components.")
    location_dest_id = fields.Many2one(
        'stock.location', 'Emplacements des produits finis',
        default=_get_default_location_dest_id,
        readonly=True,  required=True,
        states={'confirmed': [('readonly', False)]},
        help="Location where the system will stock the finished products.")
    generate_serial_visible = fields.Boolean(compute='_compute_generate_serial_visible')
    # check_to_done = fields.Boolean(compute="get_related_fields", string="Check Produced Qty")
    # procurement_group_id = fields.Many2one('procurement.group', 'Procurement Group', copy=False)

    @api.depends('production_ids.lot_producing_id', 'production_ids.product_tracking')
    def _compute_generate_serial_visible(self):
        for rec in self:
            rec.generate_serial_visible = any(p.product_tracking in ('serial', 'lot') and not p.lot_producing_id for p in rec.production_ids)

    def action_generate_serial(self):
        for p in self.mapped('production_ids').filtered(lambda p: p.product_tracking in ('serial', 'lot') and not p.lot_producing_id):
            p.action_generate_serial()

    @api.depends('production_ids.date_planned_start')
    def _compute_date_planned_start(self):
        for rec in self:
            rec.date_planned_start = min(rec.production_ids.filtered('date_planned_start').mapped('date_planned_start'), default=rec.date_planned_start or False)

    def _set_date_planned_start(self):
        for rec in self:
            rec.production_ids.date_planned_start = rec.date_planned_start

    @api.depends('production_ids.date_deadline')
    def _compute_date_deadline(self):
        for rec in self:
            rec.date_deadline = min(rec.production_ids.filtered('date_deadline').mapped('date_deadline'), default=rec.date_deadline or False)

    def _set_date_deadline(self):
        for rec in self:
            rec.production_ids.date_deadline = rec.date_deadline

    @api.depends('production_ids.confirm_cancel')
    def _compute_confirm_cancel(self):
        for rec in self:
            rec.confirm_cancel = any(x.confirm_cancel for x in rec.production_ids)

    @api.onchange('picking_type_id')
    def onchange_picking_type_id(self):
        self.location_src_id = self.picking_type_id.default_location_src_id.id
        self.location_dest_id = self.picking_type_id.default_location_dest_id.id

    @api.depends('production_ids.state', 'production_ids.date_start', 'production_ids.date_finished')
    def get_related_fields(self):
        for rec in self:
            states = rec.production_ids.mapped('state')
            rec.state = 'draft' if 'draft' in states or states == [] else \
                'confirmed' if 'confirmed' in states else \
                'progress' if 'progress' in states else \
                'to_close' if 'to_close' in states else \
                'done' if 'done' in states else \
                'cancel'
            rec.date_start = rec.production_ids.mapped('date_start')[0] if rec.production_ids else False
            rec.date_finished = rec.production_ids.mapped('date_finished')[0] if rec.production_ids else False
            # rec.check_to_done = all(rec.production_ids.mapped('check_to_done')) if rec.production_ids else False

    @api.depends('production_ids.reserve_visible', 'production_ids.unreserve_visible')
    def _compute_unreserve_visible(self):
        for rec in self:
            rec.reserve_visible = any(x.reserve_visible for x in rec.production_ids)
            rec.unreserve_visible = any(x.unreserve_visible for x in rec.production_ids)

    @api.depends('production_ids.is_locked')
    def _compute_is_locked(self):
        for rec in self:
            rec.is_locked = any(x.is_locked for x in rec.production_ids)

    @api.depends('production_ids.is_planned')
    def _compute_is_planned(self):
        for rec in self:
            rec.is_planned = any(x.is_planned for x in rec.production_ids)

    @api.depends('production_ids.show_lock')
    def _compute_show_lock(self):
        for rec in self:
            rec.show_lock = any(x.show_lock for x in rec.production_ids)

    @api.depends('production_ids.qty_produced')
    def _get_produced_qty(self):
        for rec in self:
            rec.qty_produced = sum(rec.production_ids.mapped('qty_produced'))

    @api.depends('production_ids.qty_producing')
    def _get_producing_qty(self):
        for rec in self:
            rec.qty_producing = sum(rec.production_ids.mapped('qty_producing'))

    def get_workorder_batch_count(self):
        for rec in self:
            rec.workorder_batch_done_count = len(rec.workorder_batch_ids.filtered(lambda wob: wob.state == 'done'))
            rec.workorder_batch_count = len(rec.workorder_batch_ids)

    def action_assign(self):
        self.mapped('production_ids').action_assign()

    def button_unreserve(self):
        self.mapped('production_ids').button_unreserve()

    def button_scrap(self):
        self.mapped('production_ids').button_scrap()

    # todo: look at any and toggle all to homogeneise display
    def action_toggle_is_locked(self):
        self.mapped('production_ids').action_toggle_is_locked()

    def button_plan(self):
        for rec in self.filtered(lambda p: p.state == 'confirmed'):
            rec.move_batch_ids.action_update_move_raw_data()
            rec.production_ids.button_plan()
            workorders = rec.production_ids.mapped('workorder_ids')
            workorder_batchs = []
            for operation in workorders.mapped('operation_id'):
                workorder_batch = self.env['mrp.workorder.batch'].create({
                    'mrp_production_batch_id': rec.id,
                    'operation_id': operation.id,
                    'workcenter_id': operation.workcenter_id.id,
                })
                if workorder_batchs:
                    workorder_batchs[-1].next_work_order_batch_id = workorder_batch
                workorder_batchs += workorder_batch
                workorders.filtered(lambda w: w.operation_id == operation).write(
                    {'mrp_workorder_batch_id': workorder_batch.id})

    def button_unplan(self):
        self.mapped('production_ids').button_unplan()

    # def button_unbuild(self):
    #     for rec in self.mapped('production_ids'):
    #         rec.button_unbuild()

    @api.depends('production_ids.product_id')
    def _get_unique_attribute_values(self):
        self.attribute_value_ids = self.production_ids.mapped('product_id.product_template_attribute_value_ids').filtered(
            lambda v: not v.attribute_id.group_in_mrp_batch)

    def act_show_workorder_batchs(self):
        action = self.env.ref('mrp_production_batch.mrp_workorder_batch_action').read()[0]
        action['domain'] = "[('id','in',[" + ','.join(map(str, self.workorder_batch_ids.ids)) + "])]"
        return action

    def button_mark_done(self):
        #self.mapped('move_batch_ids').action_update_move_raw_data(True)
        return self.mapped('production_ids').button_mark_done()

    def action_confirm(self):
        for rec in self.mapped('production_ids'):
            rec.action_confirm()

    def action_cancel(self):
        for rec in self.mapped('production_ids'):
            rec.action_cancel()
        if not self.mapped('production_ids'):
            self.write({'state': 'cancel'})

    @api.model
    def create(self, values):
        if not values.get('name', False) or values['name'] == _('New'):
            values['name'] = self.env['ir.sequence'].next_by_code('mrp.production.batch') or _('New')
        if not values.get('procurement_group_id'):
            values['procurement_group_id'] = self.env["procurement.group"].create({'name': values['name']}).id
        batch = super().create(values)
        if values.get('production_ids'):
            batch.action_update_move_data()
        return batch

    def unlink(self):
        for rec in self.filtered(lambda b: b.state not in ('cancel', 'draft', 'confirmed')):
            raise Warning("Vous ne pouvez pas supprimer un Lot de fabrication qui n'est pas dans l'état annulé ou brouillon")
        return super().unlink()

    def write(self, vals):
        if vals.get('production_ids'):
            self.action_update_move_data()
        if vals.get('location_src_id'):
            for rec in self.mapped('production_ids'):
                rec.write({'location_src_id': vals['location_src_id']})
        if vals.get('location_dest_id'):
            for rec in self.mapped('production_ids'):
                rec.write({'location_dest_id': vals['location_dest_id']})
        return super().write(vals)

    def action_update_move_data(self):
        self.mapped('move_batch_ids').unlink()
        for rec in self:
            move_raw_ids = rec.production_ids.mapped('move_raw_ids')
            product_ids = move_raw_ids.mapped('product_id')
            rec.move_batch_ids = [(0, 0, {
                'product_id': p.id,
                'uom_id': p.uom_id.id,
                'product_uom_qty': sum(move_raw_ids.filtered(lambda m: m.product_id == p).mapped('product_uom_qty')),
            }) for p in product_ids]
