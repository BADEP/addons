from odoo import models, api
from odoo.tools import safe_eval

class IrActions(models.Model):
    _inherit = 'ir.actions.actions'

    @api.model
    def _get_eval_context(self, action=None):
        res = super(IrActions, self)._get_eval_context(action=action)
        res.update({
            'requests': safe_eval.wrap_module(__import__('requests'), ['head', 'get', 'post', 'delete', 'put'])
        })
        return res