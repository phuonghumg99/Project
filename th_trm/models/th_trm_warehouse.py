from odoo import fields, models, api


class ThTrmWarehouse(models.Model):
    _name = "th.trm.warehouse"
    _inherit = 'mail.thread'
    _description = "Kho giảng viên"

    name = fields.Char(string="Họ và tên" ,required=True, tracking=True)