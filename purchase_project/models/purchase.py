from odoo import models, fields, api

class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    task_id = fields.Many2one(
        'project.task',
        string='Tâche',
        domain='[("project_id", "=", project_id)]'
    )
    project_id = fields.Many2one('project.project', string='Projet', required=False)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Compte analytique', related='project_id.analytic_account_id', readonly=True)

    @api.onchange('project_id')
    def onchange_project_id(self):
        for rec in self.filtered(lambda r: r.project_id):
            rec.task_id = False

    @api.onchange('analytic_account_id')
    def onchange_analytic_account_id(self):
        for line in self.order_line:
            line.account_analytic_id = self.analytic_account_id

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    @api.depends('product_id', 'date_order', 'order_id.analytic_account_id')
    def _compute_account_analytic_id(self):
        super()._compute_account_analytic_id()
        for rec in self:
            if rec.order_id.analytic_account_id:
                rec.account_analytic_id = rec.order_id.analytic_account_id