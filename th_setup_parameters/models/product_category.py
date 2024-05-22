import json
from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ProductCategory(models.Model):
    _inherit = 'product.category'

    th_module_ids = fields.Many2many(comodel_name="therp.module", string="Module",)
    th_origin_ids = fields.Many2many(comodel_name="th.origin", string="Xuất xứ")

    @api.onchange('parent_id')
    def onchange_parent_id(self):
        if self.parent_id:
            self.th_module_ids = [(6, 0, self.parent_id.th_module_ids.ids)]
            self.th_origin_ids = [(6, 0, self.parent_id.th_origin_ids.ids)]

    def write(self, values):
        module_old_ids = False
        origin_old_ids = False
        for rec in self:
            module_old_ids = rec.th_module_ids.ids
            origin_old_ids = rec.th_origin_ids.ids
        res = super(ProductCategory, self).write(values)
        if values.get('th_module_ids') or values.get('th_origin_ids'):
            for rec in self:
                for child in rec.child_id:
                    if values.get('th_module_ids'):
                        if len(module_old_ids) > len(rec.th_module_ids.ids) and rec.child_id:
                            for module in list(set(module_old_ids) - set(rec.th_module_ids.ids)) + list(set(rec.th_module_ids.ids) - set(module_old_ids)):
                                child.th_module_ids = [(3, module)]
                        if len(module_old_ids) < len(rec.th_module_ids.ids):
                            child.th_module_ids = [(4, module_id) for module_id in
                                list(set(child.th_module_ids.ids) - set(rec.th_module_ids.ids)) + list(set(rec.th_module_ids.ids) - set(child.th_module_ids.ids))]
                    if values.get('th_origin_ids'):
                        if len(origin_old_ids) > len(rec.th_origin_ids.ids) and rec.child_id:
                            for origin in list(set(origin_old_ids) - set(rec.th_origin_ids.ids)) + list(set(rec.th_origin_ids.ids) - set(origin_old_ids)):
                                child.th_origin_ids = [(3, origin)]
                        if len(origin_old_ids) < len(rec.th_origin_ids.ids):
                            child.th_origin_ids = [(4, origin_id) for origin_id in
                                list(set(child.th_origin_ids.ids) - set(rec.th_origin_ids.ids)) + list(set(rec.th_origin_ids.ids) - set(child.th_origin_ids.ids))]
        return res