from odoo import fields, models, api

class TRMStatusCategory(models.Model):
    _inherit = "th.status.category"

    th_trm_level_category = fields.Many2many(comodel_name="th.trm.stage", relation="trm_level_th_status_category_rel", column1="trm_status_category_id", column2="trm_level_category_id", string="Mối quan hệ (TRM)")
