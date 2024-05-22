import logging
from odoo import api, fields, models, Command

_logger = logging.getLogger(__name__)


class PortalWizard(models.TransientModel):
    _inherit = 'portal.wizard'

    def th_default_partner_ids(self):
        params = self.env.context.get('params', False)
        model = params.get('model', False) if params else False or self.env.context.get('active_model', False)
        contact_ids = set()
        if model:
            if model == 'prm.lead':
                prm_contact = self.env.context.get('active_ids', [])
                for prm_lead in self.env['prm.lead'].sudo().browse(prm_contact):
                    partner_ids = prm_lead.th_partner_id
                    partner = prm_lead.th_partner_id
                    contact_partners = partner.child_ids.filtered(lambda p: p.type in ('contact', 'other')) | partner
                    contact_ids |= set(contact_partners.ids)

            elif model == 'pom.lead':
                prm_contact = self.env.context.get('active_ids', [])
                for prm_lead in self.env['pom.lead'].sudo().browse(prm_contact):
                    partner_ids = prm_lead.th_partner_id
                    partner = prm_lead.th_partner_id
                    contact_partners = partner.child_ids.filtered(lambda p: p.type in ('contact', 'other')) | partner
                    contact_ids |= set(contact_partners.ids)

            elif model == 'res.partner':
                partner_ids = self.env.context.get('default_partner_ids', []) or self.env.context.get('active_ids', [])
                for partner in self.env['res.partner'].sudo().browse(partner_ids):
                    contact_partners = partner.child_ids.filtered(lambda p: p.type in ('contact', 'other')) | partner
                    contact_ids |= set(contact_partners.ids)

                return [Command.link(contact_id) for contact_id in contact_ids]

        return [Command.link(contact_id) for contact_id in contact_ids]

    partner_ids = fields.Many2many('res.partner', string='Partners', default=th_default_partner_ids)
