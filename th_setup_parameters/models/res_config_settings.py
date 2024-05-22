from odoo import models, fields, api

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    th_check_partner = fields.Boolean(string="Kiểm tra khi tạo liên hệ")

    def set_values(self):
        super().set_values()
        self.env['ir.config_parameter'].set_param('th_check_partner', self.th_check_partner)

    @api.model
    def get_values(self):
        res = super().get_values()
        res.update(th_check_partner = self.env['ir.config_parameter'].sudo().get_param('th_check_partner'))
        return res