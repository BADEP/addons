from odoo import models, api
import boto3

class IrActions(models.Model):
    _inherit = 'ir.actions.actions'

    @api.model
    def _get_eval_context(self, action=None):
        res = super(IrActions, self)._get_eval_context(action=action)
        res.update({
            'boto3': boto3
        })
        return res
