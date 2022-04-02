from odoo import models, fields, api

class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    section_id = fields.Many2one('sale.order.line', compute='_section_id', store=True)
    sub_line_ids = fields.One2many('sale.order.line', 'section_id')

    @api.depends('sequence', 'order_id.order_line', 'order_id.order_line.display_type')
    def _section_id(self):
        for rec in self:
            section_ids = rec.order_id.order_line.filtered(lambda l: l.display_type == 'line_section' and l.sequence <= rec.sequence)
            rec.section_id = section_ids and section_ids[-1] or False

    def _timesheet_service_generation(self):
        super()._timesheet_service_generation()
        lines_with_tasks = self.filtered(lambda l: l.task_id)
        #create each section in each project
        for section in lines_with_tasks.mapped('section_id'):
            child_tasks = lines_with_tasks.filtered(lambda l: l.section_id == section).mapped('task_id')
            #in case a section contains tasks in multiple projects
            for project in child_tasks.mapped('project_id'):
                parent_task = section._timesheet_create_task(project=project)
                child_tasks.filtered(lambda t: t.project_id == project).write({
                    'parent_id': parent_task.id
                })

    @api.depends('product_id.type', 'sub_line_ids')
    def _compute_is_service(self):
        for so_line in self:
            so_line.is_service = so_line.product_id.type == 'service' or \
                                 (so_line.display_type == 'line_section' and any(x.is_service for x in so_line.sub_line_ids))