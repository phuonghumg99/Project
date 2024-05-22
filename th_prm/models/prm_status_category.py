from odoo import fields, models, api

class PRMStatusCategory(models.Model):
    _inherit = "th.status.category"

    th_prm_level_category = fields.Many2many(comodel_name="prm.level", relation="prm_level_th_status_category_rel", column1="status_category_id", column2="level_category_id", string="Mối quan hệ (PRM)")
