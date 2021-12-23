from odoo import models, fields, api

class MrpProduction(models.Model):
    _name = 'mrp.production'
    _inherit = ['mrp.production', 'multi.print.mixin', 'printnode.scenario.mixin']

    def action_generate_serial(self):
        super().action_generate_serial()
        self._call_scenarios()

    def _call_scenarios(self):
        self.print_scenarios(
            action='print_production_lot_label_on_generation',
            ids_list=self.ids,
            lot_producing_id=self.lot_producing_id
        )

    def _scenario_print_production_lot_label_on_generation(self, report_id, printer_id, number_of_copies=1, **kwargs):
        lot_producing_id = kwargs.get('lot_producing_id')
        print_options = kwargs.get('options', {})
        if lot_producing_id:
            printer_id.printnode_print(
                report_id,
                lot_producing_id,
                copies=number_of_copies,
                options=print_options,
            )
            return True
        else:
            return False