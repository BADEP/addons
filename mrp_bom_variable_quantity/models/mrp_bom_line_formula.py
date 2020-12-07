from odoo import _, api, fields, models, exceptions
from odoo.tools.safe_eval import safe_eval


class MrpBomLineFormula(models.Model):
    _name = 'mrp.bom.line.formula'

    name = fields.Char(required=True, translate=True)
    code = fields.Text(required=True, default="result = 0")

    @api.constrains('code')
    def _check_code(self):
        eval_context = {
            'env': self.env,
            'context': self.env.context,
            'user': self.env.user,
            'line': self.env['mrp.bom.line'],
            'production_id': self.env['mrp.production'],
            'quantity': 0
        }
        try:
            safe_eval(
                self.code.strip(), eval_context, mode="exec", nocopy=True
            )
        except Exception as e:
            raise exceptions.ValidationError(
                _('Error evaluating code.\nDetails: %s') % e
            )
        if 'result' not in eval_context:
            raise exceptions.ValidationError(_('No valid result returned.'))

    def execute(self, eval_context):
        safe_eval(
            self.code.strip(),
            eval_context,
            mode="exec",
            nocopy=True,
        )
        return eval_context.get('result', 0)