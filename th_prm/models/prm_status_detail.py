from odoo import fields, models, api

class PRMStatusDetail(models.Model):
    _inherit = "th.status.detail"

    th_prm_level = fields.Many2many(comodel_name="prm.level", relation="prm_level_th_status_detail_rel", column1="status_detail_id", column2="level_id", string="Mối quan hệ (PRM)")
