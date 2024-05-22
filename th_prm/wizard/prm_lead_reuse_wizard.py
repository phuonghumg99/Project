from odoo import fields, models, _, api


class PRMLeadReuse(models.TransientModel):
    _name = "prm.lead.reuse"
    _description = "Tái sử dụng lead"

    name = fields.Char(string="Tên nguồn tái sử dụng", required=True)
    th_team_user = fields.Selection(string="Giao cho", selection=[('team', 'Đội nhóm'), ('individual', 'Cá nhân')], required=True)
    th_team_id = fields.Many2one(comodel_name="prm.team", string="Đội", domain="[('id', 'in', th_allowed_team_ids)]")
    th_user_id = fields.Many2one(comodel_name="res.users", string="Nhân viên", domain="[('id', 'in', th_allowed_user_ids)]")
    th_allowed_team_ids = fields.Many2many(comodel_name="prm.team", compute="_compute_th_allowed_team_ids", store=True)
    th_allowed_user_ids = fields.Many2many(comodel_name="res.users", compute="_compute_th_allowed_user_ids", store=True)

    @api.depends('th_user_id')
    def _compute_th_allowed_team_ids(self):
        for rec in self:
            if self.env.user.has_group('th_prm.group_prm_administrator'):
                user_teams = self.env['prm.team'].search([])
            else:
                user_teams = self.env['prm.team'].search([('manager_id', '=', [self.env.user.id])])

            rec.th_allowed_team_ids = user_teams.ids

    @api.depends('th_user_id')
    def _compute_th_allowed_user_ids(self):
        for rec in self:
            if self.env.user.has_group('th_prm.group_prm_administrator'):
                member_id = self.env['res.users'].search([])
            else:
                member_id = self.env['prm.team'].search([('manager_id', '=', [self.env.user.id])]).th_member_ids

            rec.th_allowed_user_ids = member_id.ids

    def open_lead(self):
        context = {
            'active_ids': self._context.get('active_ids'),
            'th_team_user': self.th_team_user,
            'th_team_id': self.th_team_id,
            'user_id': self.th_user_id,
            'model_name': self._context.get('model_name'),
            'vals': {'th_reuse_source': self.name, 'th_storage': False},
        }
        self.env['prm.assign.leads'].with_context(context).action_assign_leads()
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }
