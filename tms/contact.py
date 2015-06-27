from openerp import fields, models, api

class res_country_state_city(models.Model):
    _name = 'res.country.state.city'
    
    name = fields.Char()
    _rec_name = 'name'
    display_name = fields.Char(compute='get_name')
    state = fields.Many2one('res.country.state', required=True)
    country = fields.Many2one('res.country', related='state.country_id', readonly=True)
    
    @api.one
    def get_name(self):
        self.display_name = self.name
        return self.name
res_country_state_city()

class res_partner(models.Model):
    _inherit = 'res.partner'
    
    city = fields.Many2one('res.country.state.city')
    
    @api.model
    def _display_address(self, address, without_company=False):

        '''
        The purpose of this function is to build and return an address formatted accordingly to the
        standards of the country where it belongs.

        :param address: browse record of the res.partner to format
        :returns: the address formatted in a display that fit its country habits (or the default ones
            if not country is specified)
        :rtype: string
        '''

        # get the information that will be injected into the display format
        # get the address format
        address_format = address.country_id.address_format or \
              "%(street)s\n%(street2)s\n%(city_name)s %(state_code)s %(zip)s\n%(country_name)s"
        args = {
            'state_code': address.state_id.code or '',
            'state_name': address.state_id.name or '',
            'country_code': address.country_id.code or '',
            'country_name': address.country_id.name or '',
            'company_name': address.parent_name or '',
            'city_name': address.city.name or '',
        }
        for field in self._address_fields():
            args[field] = getattr(address, field) or ''
        if without_company:
            args['company_name'] = ''
        elif address.parent_id:
            address_format = '%(company_name)s\n' + address_format
        return address_format % args
    
    @api.one
    @api.onchange('city')
    def onchange_city(self):
        self.state_id = self.city.state
res_partner()