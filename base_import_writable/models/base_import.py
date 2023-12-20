
import codecs
import itertools
import logging


from odoo import api, fields, models
from odoo.tools.translate import _

FIELDS_RECURSION_LIMIT = 3

class Import(models.TransientModel):

    _inherit = 'base_import.import'

    @api.model
    def get_fields_tree(self, model, depth=FIELDS_RECURSION_LIMIT):
        Model = self.env[model]
        importable_fields = [{
            'id': 'id',
            'name': 'id',
            'string': _("External ID"),
            'required': False,
            'fields': [],
            'type': 'id',
        }]
        if not depth:
            return importable_fields

        model_fields = Model.fields_get()
        blacklist = models.MAGIC_COLUMNS + [Model.CONCURRENCY_CHECK_FIELD]
        for name, field in model_fields.items():
            if name in blacklist:
                continue
            if field.get('deprecated', False) is not False:
                continue
            if field.get('readonly') and field.get('compute') and not field.get('inverse'):
                states = field.get('states')
                if not states:
                    continue
                # states = {state: [(attr, value), (attr2, value2)], state2:...}
                if not any(attr == 'readonly' and value is False
                           for attr, value in itertools.chain.from_iterable(states.values())):
                    continue
            field_value = {
                'id': name,
                'name': name,
                'string': field['string'],
                # Y U NO ALWAYS HAS REQUIRED
                'required': bool(field.get('required')),
                'fields': [],
                'type': field['type'],
                'model_name': model
            }

            if field['type'] in ('many2many', 'many2one'):
                field_value['fields'] = [
                    dict(field_value, name='id', string=_("External ID"), type='id'),
                    dict(field_value, name='.id', string=_("Database ID"), type='id'),
                ]
                field_value['comodel_name'] = field['relation']
            elif field['type'] == 'one2many':
                field_value['fields'] = self.get_fields_tree(field['relation'], depth=depth-1)
                if self.user_has_groups('base.group_no_one'):
                    field_value['fields'].append({'id': '.id', 'name': '.id', 'string': _("Database ID"), 'required': False, 'fields': [], 'type': 'id'})
                field_value['comodel_name'] = field['relation']

            importable_fields.append(field_value)

        # TODO: cache on model?
        return importable_fields