from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = "res.users"

    # prm_team_id = fields.Many2one('prm.team', string='Đội prm', store=True)
    th_team_leader_ids = fields.Many2many(comodel_name="res.users", relation="th_prm_leader_ref", column1="th_prm_user", column2="th_prm_leader", string="Đội trưởng", store=True)

    # def write(self, vals):
    #     # Add code here
    #     log_portal_access = 'groups_id' in vals and not self._context.get(
    #         'mail_create_nolog') and not self._context.get('mail_notrack')
    #     user_portal_access_dict = {
    #         user.id: user.has_group('base.group_portal')
    #         for user in self
    #     } if log_portal_access else {}
    #     res = super(ResUsers, self).write(vals)
    #     if log_portal_access:
    #         for user in self:
    #             user_has_group = user.has_group('base.group_portal')
    #             portal_access_changed = user_has_group != user_portal_access_dict[user.id]
    #             if portal_access_changed:
    #                 body = user._get_portal_access_update_body(user_has_group)
    #                 prm_partner = self.env['prm.lead'].search([('th_partner_id', '=', user.partner_id.id)], limit=1,
    #                                                           order='id DESC')
    #                 pom_partner = self.env['pom.lead'].search([('th_partner_id', '=', user.partner_id.id)], limit=1,
    #                                                           order='id DESC')
    #                 if prm_partner:
    #                     prm_partner.message_post(
    #                         body=body,
    #                         message_type='notification',
    #                         subtype_xmlid='mail.mt_note'
    #                     )
    #                 if pom_partner:
    #                     pom_partner.message_post(
    #                         body=body,
    #                         message_type='notification',
    #                         subtype_xmlid='mail.mt_note'
    #                     )
    #
    #     return res
