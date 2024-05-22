from odoo import models, fields

class ThReligion(models.Model):
    _name = 'th.religion'
    _description = 'Tôn giáo'

    name = fields.Char(string='Tôn giáo', required=True)