import datetime

from odoo import models, fields, api, _, SUPERUSER_ID


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    mrp_production_batch_id = fields.Many2one('mrp.production.batch')

    def get_suitable_batches(self, vals):
        batches = self.env['mrp.production.batch'].search([
            ('state', '=', 'draft'),
            ('picking_type_id', '=', vals.get('picking_type_id')),
            ('routing_id', '=', vals.get('routing_id')),
            # ('origin', '=', production.origin)
        ])
        attribute_values = self.env['product.product'].browse(vals['product_id']).product_template_attribute_value_ids.filtered(lambda v: not v.attribute_id.group_in_mrp_batch)
        return batches.filtered(lambda b: attribute_values in b.attribute_value_ids or attribute_values == b.attribute_value_ids)

    @api.model
    def create(self, vals):
        if not vals.get('mrp_production_batch_id'):
            batches = self.get_suitable_batches(vals)
            if batches:
                batch = batches[0]
            else:
                batch = self.env['mrp.production.batch'].create({
                    'origin': vals.get('origin'),
                    'routing_id': vals.get('routing_id'),
                    'date_planned_start': vals.get('date_planned_start'),
                    'date_planned_finished': vals.get('date_planned_finished'),
                    'user_id': vals.get('user_id'),
                    'company_id': vals.get('company_id'),
                    'picking_type_id': vals.get('picking_type_id'),
                    'location_src_id': vals.get('location_src_id'),
                    'location_dest_id': vals.get('location_dest_id'),
                })

            vals.update({
                'mrp_production_batch_id': batch.id,
                'procurement_group_id': batch.procurement_group_id.id
            })
        else:
            vals.update({
                'procurement_group_id': self.env['mrp.production.batch'].browse(vals['mrp_production_batch_id']).procurement_group_id.id
            })
        production = super().create(vals)
        production.mrp_production_batch_id.action_update_move_data()
        return production


class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    mrp_workorder_batch_id = fields.Many2one('mrp.workorder.batch', string='Lot de travail')

class MrpWorkcenter(models.Model):
    _inherit = 'mrp.workcenter'

    batch_order_ids = fields.One2many('mrp.workorder.batch', 'workcenter_id', "Batch Orders")

    # todo: fix me
    # @api.depends('batch_order_ids.duration_expected', 'batch_order_ids.workcenter_id', 'batch_order_ids.state', 'batch_order_ids.date_planned_start')
    # def _compute_workorder_count(self):
    #     MrpWorkorderBatch = self.env['mrp.workorder.batch']
    #     result = {wid: {} for wid in self.ids}
    #     result_duration_expected = {wid: 0 for wid in self.ids}
    #     #Count Late Workorder
    #     data = MrpWorkorderBatch.read_group([('workcenter_id', 'in', self.ids), ('state', 'in', ('pending', 'ready')), ('date_planned_start', '<', datetime.datetime.now().strftime('%Y-%m-%d'))], ['workcenter_id'], ['workcenter_id'])
    #     count_data = dict((item['workcenter_id'][0], item['workcenter_id_count']) for item in data)
    #     #Count All, Pending, Ready, Progress Workorder
    #     res = MrpWorkorderBatch.read_group(
    #         [('workcenter_id', 'in', self.ids)],
    #         ['workcenter_id', 'state', 'duration_expected'], ['workcenter_id', 'state'],
    #         lazy=False)
    #     for res_group in res:
    #         result[res_group['workcenter_id'][0]][res_group['state']] = res_group['__count']
    #         if res_group['state'] in ('pending', 'ready', 'progress'):
    #             result_duration_expected[res_group['workcenter_id'][0]] += res_group['duration_expected']
    #     for workcenter in self:
    #         workcenter.workorder_count = sum(count for state, count in result[workcenter.id].items() if state not in ('done', 'cancel'))
    #         workcenter.workorder_pending_count = result[workcenter.id].get('pending', 0)
    #         workcenter.workorder_ready_count = result[workcenter.id].get('ready', 0)
    #         workcenter.workorder_progress_count = result[workcenter.id].get('progress', 0)
    #         workcenter.workorder_late_count = count_data.get(workcenter.id, 0)
