from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    purchase_ids = fields.One2many('purchase.order', 'task_id', 'Achats')
    purchase_order_count = fields.Integer(
        compute='_purchase_order_count',
        string="Achats",
        store=True,
    )

    @api.depends('purchase_ids')
    def _purchase_order_count(self):
        for rec in self:
            rec.purchase_order_count = len(rec.purchase_ids)

    def view_purchase_order(self):
        for rec in self:
            res = self.env.ref('purchase.purchase_rfq')
            res = res.read()[0]
            res['domain'] = str([('id', 'in', rec.purchase_ids.ids)])
        return res
