from odoo import fields, models

class PRMPartnerLevel(models.Model):
    _name = "prm.partner.level"
    _description = "Cấp đối tác"

    name = fields.Char(string="Loại", required=True)
    th_description = fields.Char(string="Mô tả")


