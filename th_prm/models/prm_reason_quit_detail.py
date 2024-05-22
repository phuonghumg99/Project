from odoo import fields, models

class PRMReasonQuitDetail(models.Model):
    _name = "prm.reason.quit.detail"
    _description = "Chi tiết lý do ngừng hợp tác"

    name = fields.Char(string="Tên", required=True)
    th_reason_quit_id = fields.Many2one(comodel_name="prm.reason.quit")
    th_description = fields.Char(string="Mô tả")
