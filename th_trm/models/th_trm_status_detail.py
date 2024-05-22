from odoo import fields, models

class ThTrmStatusDetail(models.Model):
    _inherit = "th.status.detail"

    th_trm_level_ids = fields.Many2many(comodel_name="th.trm.stage", relation="trm_level_th_status_detail_rel", column1="trm_status_detail_id", column2="trm_level_id", string="Mối quan hệ (TRM)")