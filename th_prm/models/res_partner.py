from odoo import fields, models, api, _
from odoo.exceptions import UserError

class ResPartner(models.Model):
    _inherit = "res.partner"
    th_lead_prm_count = fields.Integer(string="Cơ hội prm",compute="_compute_th_lead_prm_count")

    def _compute_th_lead_prm_count(self):
        for rec in self:
            rec.th_lead_prm_count = len(self.env['prm.lead'].search([('th_partner_id', '=', rec.id)]))

    def action_view_prm_lead(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cơ hội PRM',
            'view_mode': 'tree,form',
            'res_model': 'prm.lead',
            'target': 'current',
            'domain': [('th_partner_id', '=', self.id)],
            'context': {'create': False}
        }
    def action_send_update_info(self, value):
        subject = f'Yêu cầu cập nhật thông tin'
        message = 'có yêu cầu cập nhật thông tin:'
        template_id = self.env.ref('th_prm.th_template_send_update_info')
        partner_ids = value.get('id', False)

        ctx = {
            'subject': subject,
            'message': message,
            'email_from': self.browse(int(partner_ids)).email,
            'email_to': self.env['pom.lead'].search([('th_partner_id','=', int(partner_ids))]).th_user_id.email,
            'manager': self.env['pom.lead'].search([('th_partner_id','=', int(partner_ids))]).th_user_id.name,
            'partner': self.env['res.partner'].search([('id','=', partner_ids)]).name,
            'update_info': value.get('update_info_aff', False),
        }
        template_id.with_context(ctx).send_mail(self.browse(int(partner_ids)).id, force_send=True)

