from odoo import models, fields


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    th_lecturer_profile_id = fields.Many2one('th.lecturer.profile')