from odoo import models, api, fields, modules
import requests, os

class IrModuleModule(models.Model):
    _inherit = 'ir.module.module'

    upgrade_available = fields.Boolean(string='Upgradable', compute='_upgrade_available', store=True)
    #todo: this should not be per module. Probably ir.config_parameter
    target = fields.Selection([
        ('17.0', '17.0'),
    ], default='17.0', required=False)
    alternative_name = fields.Char(string='Alternative name')
    python_lines = fields.Integer(compute='_get_module_info', store=True)
    xml_lines = fields.Integer(compute='_get_module_info', store=True)
    module_path = fields.Char(compute='_get_module_info', store=True)

    def _get_module_info(self):
        def count_lines_in_file(file_path):
            with open(file_path, 'r', encoding='utf-8') as file:
                try:
                    return sum(1 for line in file)
                except Exception:
                    return 0
        for module in self:
            module.module_path = modules.get_module_resource(module.name, '')
            xml_lines = python_lines = 0
            if module.module_path:
                for root, dirs, files in os.walk(module.module_path):
                    for file in files:
                        if file.endswith('.py'):
                            file_path = os.path.join(root, file)
                            python_lines += count_lines_in_file(file_path)
                        elif file.endswith('.xml'):
                            file_path = os.path.join(root, file)
                            xml_lines += count_lines_in_file(file_path)
            module.xml_lines = xml_lines
            module.python_lines = python_lines

    def action_check_upgrade(self):
        self._get_module_info()
        self._upgrade_available()

    @api.depends('target', 'alternative_name', 'state')
    def _upgrade_available(self):
        records = self if self.ids else self.search([('upgrade_available', '=', False)])
        for rec in records.filtered(lambda x: x.state != 'installed'):
            rec.upgrade_available = False
        for rec in records.filtered(lambda x: x.state == 'installed'):
            rec.upgrade_available = False
            if not rec.target:
                rec.target = '17.0'
            if rec.author == 'Odoo S.A.':
                rec.upgrade_available = True
            else:
                try:
                    r = requests.head("https://apps.odoo.com/apps/modules/%s/%s" % (rec.target, rec.alternative_name if rec.alternative_name else rec.name))
                    if r.status_code == 200:
                        rec.upgrade_available = True
                    else:
                        r = requests.get(f'https://pypi.org/pypi/odoo%s-addon-%s/json' % ('' if int(rec.target[:2]) >= 15  else rec.target.replace('.0', ''),
                                                                                   (rec.alternative_name if rec.alternative_name else rec.name).replace('_', '-')))
                        if r.status_code == 200:
                            releases = r.json()['releases'].keys()
                            if any([x[:4] == rec.target for x in releases]):
                                rec.upgrade_available = True
                        else:
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
                except requests.ConnectionError:
                    pass

    def action_force_compute_upgrade(self):
        self._upgrade_available()

class IrModuleRepo(models.Model):
    _name = 'ir.module.repo'
    _description = 'Modules GIT repository'

    name = fields.Char(required=True)
    subpath = fields.Char()
    username = fields.Char()
    token = fields.Char()
