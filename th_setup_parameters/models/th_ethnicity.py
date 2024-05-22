from odoo import models, fields

class ThEthnicity(models.Model):
    _name = 'th.ethnicity'
    _description = 'Dân tộc'

    name = fields.Char(string='Dân tộc', required=True)