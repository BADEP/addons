from dateutil.relativedelta import relativedelta

from odoo import models, fields, api, _


class MrpWorkorderBatch(models.Model):
    _name = 'mrp.workorder.batch'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    workcenter_id = fields.Many2one(
        'mrp.workcenter', 'Work Center', required=True,
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    working_state = fields.Selection(
        'Workcenter Status', related='workcenter_id.working_state', readonly=False,
        help='Technical: used in views only')
    production_state = fields.Selection(
        'Production State', readonly=True,
        related='mrp_production_batch_id.state',
        help='Technical: used in views only.')
    is_first_wob = fields.Boolean(string="Is the first WOB to produce",
                                  compute='_compute_is_first_wob')
    state = fields.Selection([
        ('pending', 'Pending'),
        ('ready', 'Ready'),
        ('progress', 'In Progress'),
        ('done', 'Finished'),
        ('cancel', 'Cancelled')], string='Status', compute='get_related_fields', store=True)
    date_planned_start = fields.Datetime(
        'Scheduled Date Start',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    date_planned_finished = fields.Datetime(
        'Scheduled Date Finished',
        states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})
    date_start = fields.Datetime(
        'Effective Start Date', compute='get_related_fields', store=True)
    date_finished = fields.Datetime(
        'Effective End Date', compute='get_related_fields', store=True)
    #time_ids = fields.One2many('mrp.workcenter.productivity', compute='get_related_fields')
    duration_expected = fields.Float(
        'Expected Duration', digits=(16, 2), help="Expected duration (in minutes)", compute='_compute_duration',
        store=True)
    duration = fields.Float(
        'Real Duration', compute='_compute_duration',
        readonly=True, store=True)
    duration_unit = fields.Float(
        'Duration Per Unit', compute='_compute_duration',
        group_operator="avg", readonly=True, store=True)
    duration_percent = fields.Integer(
        'Duration Deviation (%)', compute='_compute_duration',
        group_operator="avg", readonly=True, store=True)
    name = fields.Char(compute='get_name')
    workorder_ids = fields.One2many('mrp.workorder', 'mrp_workorder_batch_id')
    operation_id = fields.Many2one('mrp.routing.workcenter', 'Operation', required=True, ondelete='cascade')
    mrp_production_batch_id = fields.Many2one('mrp.production.batch', required=True)
    is_user_working = fields.Boolean(
        'Is the Current User Working', compute='get_related_fields',
        help="Technical field indicating whether the current user is working. ")
    working_user_ids = fields.One2many('res.users', string='Working user on this work order.',
                                       compute='get_related_fields')
    next_work_order_batch_id = fields.Many2one('mrp.workorder.batch', "Next Work Order")
    is_produced = fields.Boolean(string="Has Been Produced",
                                 compute='get_related_fields')

    @api.depends('workorder_ids.state', 'workorder_ids.date_start', 'workorder_ids.date_finished',
                 'workorder_ids.is_produced', 'workorder_ids.time_ids', 'workorder_ids.working_user_ids')
    def get_related_fields(self):
        for rec in self.filtered(lambda b: b.workorder_ids):
            rec.date_start = rec.workorder_ids.mapped('date_start')[0]
            rec.date_finished = rec.workorder_ids.mapped('date_finished')[0]
            rec.state = rec.workorder_ids.mapped('state')[0]
            rec.is_produced = all(rec.workorder_ids.sudo().mapped('is_produced'))
            #rec.time_ids = rec.workorder_ids.mapped('time_ids')
            rec.working_user_ids = rec.workorder_ids.mapped('working_user_ids')
            rec.is_user_working = any([order.is_user_working for order in rec.workorder_ids])

    def _compute_is_first_wob(self):
        for wob in self:
            wob.is_first_wob = (wob.mrp_production_batch_id.workorder_batch_ids[0] == wob)

    @api.depends('workorder_ids')
    def _compute_duration(self):
        for rec in self:
            if rec.workorder_ids:
                rec.duration = sum(rec.workorder_ids.mapped('duration'))
                rec.duration_unit = max(rec.workorder_ids.mapped('duration_unit'))
                rec.duration_expected = sum(rec.workorder_ids.mapped('duration_expected'))
            if rec.duration_expected:
                rec.duration_percent = 100 * (rec.duration_expected - rec.duration) / rec.duration_expected
            else:
                rec.duration_percent = 0

    @api.onchange('date_planned_start', 'duration_expected')
    def _onchange_date_planned_finished(self):
        if self.date_planned_start and self.duration_expected:
            self.date_planned_finished = self.date_planned_start + relativedelta(minutes=self.duration_expected)

    def record_production(self):
        for wo in self.mapped('workorder_ids').filtered(lambda w: w.state == 'progress'):
            wo.record_production()

    def get_name(self):
        for rec in self:
            rec.name = rec.mrp_production_batch_id.name + ' - ' + rec.operation_id.name

    def button_start(self):
        for rec in self.workorder_ids:
            rec.button_start()

    def button_finish(self):
        for rec in self.workorder_ids.filtered(lambda w: w.state == 'progress'):
            rec.button_finish()

    def button_pending(self):
        for rec in self.workorder_ids:
            rec.button_pending()

    def button_unblock(self):
        self.workorder_ids.mapped('workcenter_id').unblock()

    def action_cancel(self):
        self.workorder_ids.action_cancel()

    def button_done(self):
        self.workorder_ids.button_done()
