from odoo import models, fields, api, _


class TrmResPartner(models.Model):
    _inherit = 'res.partner'
    th_lead_trm_count = fields.Integer(string="Cơ hội trm", compute="_compute_th_lead_trm_count")

    def _compute_th_lead_trm_count(self):
        for rec in self:
            rec.th_lead_trm_count = self.env['th.lecturer.profile'].search([('th_partner_id', '=', self.id)]).th_quantity

    def action_view_trm_lead(self):
        self.ensure_one()
        action = self.env['th.lecturer.profile'].search([('th_partner_id', '=', self.id)]).action_open_registered_subject()
        action['target'] = 'current'
        return action

    @api.model
    def default_get(self, field_list):
        result = super().default_get(field_list)
        if self._context.get('trm_contact'):
            result['th_module_ids'] = [[6, 0, [self.env.ref('th_setup_parameters.th_trm_module').id]]]
        return result
     
