from odoo import _, api, fields, models, exceptions
from odoo.tools.safe_eval import safe_eval
DEFAULT_PYTHON_CODE = """# Available variables:
#  - env: Odoo Environment
#  - context: Context
#  - production_id: Production Order
#  - quantity: Production Quantity
#  - line: BoM Line
#  - user: Connected user
#  - result: return result
result = quantity\n\n\n\n"""

class MrpBomLineFormula(models.Model):
    _name = 'mrp.bom.line.formula'
    _description = 'BoM Line Formula'

    name = fields.Char(required=True, translate=True)
    code = fields.Text(required=True, default=DEFAULT_PYTHON_CODE)

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

    # get extra_data to be injected directly into the raw move
    def execute_extra_data(self, eval_context):
        safe_eval(
            self.code.strip(),
            eval_context,
            mode="exec",
            nocopy=True,
        )
        return eval_context.get('extra_data', 0)