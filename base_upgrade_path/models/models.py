from odoo import models, api, fields, modules
import requests

class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    upgrade_available = fields.Boolean(string='Upgradable', compute='_upgrade_available', store=True)
    #todo: this should not be per module. Probably ir.config_parameter
    target = fields.Selection([
        ('16.0', '16.0'),
    ], default='16.0', required=False)
    alternative_name = fields.Char(string='Alternative name')
    module_path = fields.Char(compute='get_module_path')

    def get_module_path(self):
        for module in self:
            module.module_path = modules.get_module_resource(module.name, '')

    @api.depends('target', 'alternative_name', 'state')
    def _upgrade_available(self):
        records = self if self.ids else self.search([('upgrade_available', '=', False)])
        for rec in records:
            rec.upgrade_available = False
            if not rec.target:
                rec.target = '15.0'
            if rec.author == 'Odoo S.A.':
                rec.upgrade_available = True
            else:
                try:
                    r = requests.head("https://apps.odoo.com/apps/modules/%s/%s/" % (rec.target, rec.alternative_name if rec.alternative_name else rec.name))
                    if r.status_code == 200:
                        rec.upgrade_available = True
                        return
                    r = requests.head("https://pypi.org/project/odoo%s-addon-%s/" % ('' if rec.target == '15.0' else rec.target.replace('.0', ''),
                                                                               (rec.alternative_name if rec.alternative_name else rec.name).replace('_', '-')))
                    if r.status_code == 200:
                        rec.upgrade_available = True
                        return

                    for repo in self.env['ir.module.repo'].search([]):
                        path = 'https://api.github.com/repos/%s/contents/' % (repo.name)
                        if repo.subpath:
                            path = path + repo.subpath + '/'
                        path = path + (rec.alternative_name if rec.alternative_name else rec.name) + ('?ref=%s' % rec.target)
                        if repo.token:
                            data = requests.get(path, auth=(repo.username, repo.token))
                        else:
                            data = requests.get(path)
                        if data.status_code == 200:
                            rec.upgrade_available = True
                            return
                except requests.ConnectionError:
                    return

    def action_force_compute_upgrade(self):
        self._upgrade_available()

class IrModuleRepo(models.Model):
    _name = 'ir.module.repo'
    _description = 'Modules GIT repository'

    name = fields.Char(required=True)
    subpath = fields.Char()
    username = fields.Char()
    token = fields.Char()