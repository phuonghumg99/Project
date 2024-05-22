import json
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    th_product_category_domain_1 = fields.Char(compute='_compute_product_categ')

    @api.depends('categ_id')
    def _compute_product_categ(self):
        domain = []
        if self.categ_id and self._context.get('view_product_crm', False):
            module_ids = self.env.ref('th_setup_parameters.th_crm_module').ids
            categ_id = self.env['product.category'].search([('th_module_ids', '=', module_ids)])
            domain.append(('id', 'in', categ_id.ids))
        if self.categ_id and self._context.get('view_product_apm', False):
            module_ids = self.env.ref('th_setup_parameters.th_apm_module').ids
            categ_id = self.env['product.category'].search([('th_module_ids', '=', module_ids)])
            domain.append(('id', 'in', categ_id.ids))
        self.th_product_category_domain_1 = json.dumps(domain)