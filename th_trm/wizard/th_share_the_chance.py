from odoo import _, fields, models, api, exceptions
import json

class ShareTheChance(models.TransientModel):
    _name = "th.share.the.chance"
    _description = 'Chia cơ hội'

    th_team_user = fields.Selection(string="Chia cơ hội", selection=[('team', 'Đội nhóm'), ('individual', 'Cá nhân')] , default="team")
    th_user_id = fields.Many2one(comodel_name="res.users", string="Cá nhân")
    th_team_id = fields.Many2one(comodel_name="th.trm.team" ,string="Đội nhóm")

    @api.onchange('th_team_user')
    def _onchange_team_or_user(self):
        if self.th_team_user == 'team':
            self.th_user_id = False
        if self.th_team_user == 'individual':
            self.th_team_id = False

    def action_share_the_chance(self):
        active_ids = self._context.get('active_ids')
        model_name = self._context.get('active_model') or self._name
        if not active_ids or model_name not in ('th.trm.lead'):
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
                vals['th_user_id'] = member_ids[flag]
                self.env[model_name].browse(active_id).write(vals)
                flag = (flag + 1) % len(member_ids)
            th_team_id.th_flag = json.dumps([flag, member_ids[flag]])
        if th_team_user == 'individual':
            user_id = self._context.get('user_id') or self.th_user_id
            for active_id in active_ids:
                vals['th_user_id'] = user_id.id
                self.env[model_name].browse(active_id).write(vals)