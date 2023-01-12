from odoo import models, fields, api


class ProjectTask(models.Model):
    _inherit = 'project.task'

    purchase_request_ids = fields.One2many('purchase.request', 'task_id', 'Demandes d\'achat')
    purchase_request_count = fields.Integer(
        compute='_purchase_request_count',
        string="Demandes d\'achat",
        store=True,
    )

    @api.depends('purchase_request_ids')
    def _purchase_request_count(self):
        for rec in self:
            rec.purchase_request_count = len(rec.purchase_request_ids)

    def view_purchase_request(self):
        for rec in self:
            res = self.env.ref('purchase_request.purchase_request_form_action')
            res = res.read()[0]
            res['domain'] = str([('id', 'in', rec.purchase_request_ids.ids)])
        return res
