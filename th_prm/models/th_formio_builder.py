from odoo import fields, models, api


class ThFormioBuilder(models.Model):
    _inherit = "formio.builder"

    th_storage_location = fields.Selection(selection_add=[('prm', 'PRM')], ondelete={'prm': 'cascade'})
    th_field_default_ids = fields.One2many(comodel_name="th.formio.builder.field.default",
                                           inverse_name="th_formio_builder_id", string="Giá trị mặc định")

    @api.model
    def default_get(self, field_list):
        result = super().default_get(field_list)
        # if self._context.get('view_product_apm', False) and not result.get('project_id'):
        result['th_field_default_ids'] = [(0, 0, {'th_default_value': "Giá trị mặc định"})]
        return result
