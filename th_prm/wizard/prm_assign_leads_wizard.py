import xmlrpc

from odoo import _, fields, models, api, exceptions
import json

class PRMAssignLeadsToTeam(models.TransientModel):
    _name = 'prm.assign.leads'
    _description = 'Giao tập lead cho nhóm hoặc thành viên'

    th_team_user = fields.Selection(string="Giao cho", selection=[('team', 'Đội nhóm'), ('individual', 'Cá nhân')], default="team")
    th_team_id = fields.Many2one(comodel_name="prm.team", string="Đội", domain="[('id', 'in', th_allowed_team_ids)]")
    th_user_id = fields.Many2one(comodel_name="res.users", string="Nhân viên", domain="[('id', 'in', th_allowed_user_ids)]")
    th_allowed_team_ids = fields.Many2many(comodel_name="prm.team", compute="_compute_th_allowed_team_ids", store=True)
    th_allowed_user_ids = fields.Many2many(comodel_name="res.users", compute="_compute_th_allowed_user_ids", store=True)

    @api.depends('th_user_id')
    def _compute_th_allowed_team_ids(self):
        for rec in self:
            if self.env.user.has_group('th_prm.group_prm_user'):
                user_teams = self.env['prm.team'].search([])
            else:
                user_teams = self.env['prm.team'].search([('manager_id', '=', [self.env.user.id])])

            rec.th_allowed_team_ids = user_teams.ids

    @api.depends('th_user_id')
    def _compute_th_allowed_user_ids(self):
        for rec in self:
            if self.env.user.has_group('th_prm.group_prm_user'):
                member_id = self.env['res.users'].search([('groups_id', '=', self.env.ref('th_prm.group_prm_user').id)])
            else:
                member_id = self.env['prm.team'].search([('manager_id', '=', [self.env.user.id])]).th_member_ids

            rec.th_allowed_user_ids = member_id.ids

    @api.onchange('th_team_user')
    def _onchange_team_or_user(self):
        if self.th_team_user == 'team':
            self.th_user_id = False
        if self.th_team_user == 'individual':
            self.th_team_id = False

    def action_assign_leads(self):
        active_ids = self._context.get('active_ids')
        model_name = self._context.get('model_name') or self._context.get('active_model')
        if not active_ids or model_name not in ['prm.lead', 'pom.lead']:
            return
        th_team_user = self._context.get('th_team_user') or self.th_team_user
        vals = self._context.get('vals') or {}
        if th_team_user == 'team':
            th_team_id = self._context.get('th_team_id') or self.th_team_id
            member_ids = th_team_id.th_member_ids.ids
            member_ids.sort()
            if len(member_ids) == 0:
                raise exceptions.UserError(_("Đội/Nhóm '%s' chưa có thành viên. Vui lòng thêm thành viên vào nhóm để thực hiện chức năng này", self.th_team_id.name))
            th_flag = json.loads(th_team_id.th_flag)
            flag = th_flag[0]
            for active_id in active_ids:
                if model_name == 'pom.lead':
                    self.active_user_api(self.env[model_name].browse(active_id))
                vals['th_user_id'] = member_ids[flag]
                self.env[model_name].browse(active_id).write(vals)
                flag = (flag + 1) % len(member_ids)
            th_team_id.sudo().th_flag = json.dumps([flag, member_ids[flag]])
        if th_team_user == 'individual':
            user_id = self._context.get('user_id') or self.th_user_id
            for active_id in active_ids:
                vals['th_user_id'] = user_id.id
                if model_name == 'pom.lead':
                    self.active_user_api(self.env[model_name].browse(active_id))
                self.env[model_name].browse(active_id).write(vals)

    def active_user_api(self, pom):
        server_api = self.env['th.api.server'].search([('state', '=', 'deploy'), ('th_type', '=', 'aff')], limit=1, order='id desc')
        if not server_api:
            return False
        try:
            result_apis = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(server_api.th_url_api))
            result_apis.execute_kw(server_api.th_db_api, server_api.th_uid_api, server_api.th_password,
                                   'res.partner', 'check_access_rights', ['read'], {'raise_exception': False})
            user_exists = result_apis.execute_kw(server_api.th_db_api, server_api.th_uid_api,
                                                 server_api.th_password, 'res.users', 'search_read',
                                                 [[['login', '=', pom.th_partner_email],
                                                   ['active', 'in', [False, True]]]],
                                                 {'fields': ['partner_id'], 'limit': 1})

            if user_exists:
                result_apis.execute_kw(server_api.th_db_api, server_api.th_uid_api, server_api.th_password, 'res.users', 'write', [[user_exists[0]['id']], {'active': True}])
                result_apis.execute_kw(server_api.th_db_api, server_api.th_uid_api, server_api.th_password, 'res.partner', 'write', [[user_exists[0]['partner_id'][0]], {'active': True}])
            pom.write({'th_api_state': True})
        except Exception as e:
            print(e)
            pom.write({'th_api_state': False})
