from odoo import fields, models

class ThTest(models.Model):
    _inherit = "th.ownership.unit"

    th_team_prm = fields.One2many(comodel_name="prm.team", inverse_name="th_ownership_unit_team_id" ,string="prm team")

    def action_prm_lead_ownership_unit(self):
        action = self.env["ir.actions.actions"]._for_xml_id("th_prm.action_prm_lead_view")
        action['display_name'] = self.name
        return action

    def action_pom_lead_ownership_unit(self):
        action = self.env["ir.actions.actions"]._for_xml_id("th_prm.action_pom_lead_view")
        action['display_name'] = self.name
        return action

    def action_prm_lead_reuse(self):
        action = self.env["ir.actions.actions"]._for_xml_id("th_prm.action_prm_lead_reuse_view")
        action['display_name'] = self.name
        return action

    def action_pom_lead_reuse(self):
        action = self.env["ir.actions.actions"]._for_xml_id("th_prm.action_pom_lead_reuse_view")
        action['display_name'] = self.name
        return action
