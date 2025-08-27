from odoo import models, fields, api

class PurchaseRequest(models.Model):
    _inherit = "purchase.request"

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
        for line in self.line_ids:
            line.analytic_account_id = self.analytic_account_id

class PurchaseRequestLine(models.Model):
    _inherit = 'purchase.request.line'
    analytic_account_id = fields.Many2one(
        comodel_name="account.analytic.account",
        string="Analytic Account",
        compute='_compute_account_analytic_id',
        store=True,
        readonly=False,
        tracking=True,
    )

    @api.depends('request_id.analytic_account_id')
    def _compute_account_analytic_id(self):
        for rec in self:
            if rec.request_id.analytic_account_id:
                rec.analytic_account_id = rec.request_id.analytic_account_id