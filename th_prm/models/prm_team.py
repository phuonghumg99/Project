from odoo import fields, models, _, api, exceptions
from odoo.exceptions import ValidationError
import json


class PRMTeam(models.Model):
    _name = "prm.team"
    _description = "Đội/Nhóm"
    _order = "name"
    _rec_name = 'complete_name'
    _parent_store = True

    name = fields.Char('Tên đội/nhóm', required=True)
    complete_name = fields.Char('Tên hoàn thành', compute='_compute_complete_name', recursive=True, store=True)
    active = fields.Boolean('Active', default=True)
    company_id = fields.Many2one('res.company', string='Công ty', index=True, default=lambda self: self.env.company)
    parent_id = fields.Many2one('prm.team', string='Đội/nhóm cha', index=True,
                                domain="['|', ('company_id', '=', False), ('company_id', '=', company_id), ('id', '!=', id)]")
    child_ids = fields.One2many('prm.team', 'parent_id', string='Đội/nhóm con')
    # member_ids = fields.One2many('res.users', 'prm_team_id', string='Thành viên', readonly=True)
    total_member = fields.Integer(compute='_compute_total_member', string='Tổng số thành viên')
    color = fields.Integer('Màu')
    parent_path = fields.Char(index=True, unaccent=False)
    master_team_id = fields.Many2one(
        'prm.team', 'Đội chính', compute='_compute_master_team_id', store=True)
    manager_id = fields.Many2one(comodel_name="res.users", string="Quản lý", tracking=True)
    domain_manager_id = fields.Char(string="Quản lý", compute="_compute_domain_manager_id")
    th_description = fields.Char(string="Mô tả")
    th_member_ids = fields.Many2many(comodel_name="res.users", relation="prm_team_users_rel", string="Thành viên")
    th_flag = fields.Char(string="Cờ")
    parent_member_ids = fields.Char(string="Thành viên của đội cha", compute="_compute_th_member_ids")
    th_ownership_unit_team_id = fields.Many2one("th.ownership.unit", string="Đơn vị sở hữu",
                                                compute='_compute_parent_id', store=True, recursive=True)

    @api.depends('parent_id')
    def _compute_domain_manager_id(self):
        for rec in self:
            domain = []
            if rec.parent_id:
                domain.append(
                    ['|', ('id', '=', rec.parent_id.manager_id.id), ('id', 'in', rec.parent_id.th_member_ids.ids),
                     ('groups_id', 'in', rec.env.ref('th_prm.group_prm_leader').ids),
                     ('share', '=', False)])
            else:
                domain.append([('groups_id', 'in', rec.env.ref('th_prm.group_prm_leader').ids),
                               ('share', '=', False)])
            rec.domain_manager_id = json.dumps(domain[0])

    @api.depends('parent_id.th_ownership_unit_team_id')
    def _compute_parent_id(self):
        if self.parent_id:
            self.th_ownership_unit_team_id = self.parent_id.th_ownership_unit_team_id

    @api.depends('parent_id', 'manager_id')
    def _compute_th_member_ids(self):
        for rec in self:
            domain = []
            if rec.manager_id:
                domain.append(('id', '!=', rec.manager_id.id))
            if rec.parent_id:
                member_ids = rec.parent_id.th_member_ids
                domain.append(('id', 'in', member_ids.ids))
            rec.parent_member_ids = json.dumps(domain)

    def name_get(self):
        if not self.env.context.get('hierarchical_naming', True):
            return [(record.id, record.name) for record in self]
        return super(PRMTeam, self).name_get()

    @api.model
    def name_create(self, name):
        return self.create({'name': name}).name_get()[0]

    @api.depends('name', 'parent_id.complete_name')
    def _compute_complete_name(self):
        for team in self:
            if team.parent_id:
                team.complete_name = '%s / %s' % (team.parent_id.complete_name, team.name)
            else:
                team.complete_name = team.name

    @api.depends('parent_path')
    def _compute_master_team_id(self):
        for team in self:
            team.master_team_id = int(team.parent_path.split('/')[0])

    # def _compute_total_member(self):
    #     member_data = self.env['res.users']._read_group([('prm_team_id', 'in', self.ids)], ['prm_team_id'], ['prm_team_id'])
    #     result = dict((data['prm_team_id'][0], data['prm_team_id_count']) for data in member_data)
    #     for team in self:
    #         team.total_member = result.get(team.id, 0)

    @api.constrains('parent_id')
    def _check_parent_id(self):
        if not self._check_recursion():
            raise ValidationError(_('Bạn không thể tạo phòng ban đệ quy.'))

    def get_children_team_ids(self):
        return self.env['prm.lead'].search([('id', 'child_of', self.ids)])

    @api.constrains('name')
    def _check_name_uniq(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name), ('id', '!=', rec.id)]) > 0:
                raise exceptions.ValidationError("Tên %s đã tồn tại." % rec.name)

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        flag = 0
        for team in res:
            team.th_flag = json.dumps([flag, False])
            if team.manager_id:
                # team.manager_id.prm_team_id = team.id
                for user in team.th_member_ids:
                    # user.prm_team_id = team.id
                    user.th_team_leader_ids = [(6, 0, team.manager_id.ids)]

        return res

    def write(self, vals):
        th_manager = self.manager_id
        member_ids = self.th_member_ids
        res = super().write(vals)
        for rec in self:
            for member in member_ids:
                if member not in rec.th_member_ids:
                    member.th_team_leader_ids = False
            if rec.manager_id:
                # if th_manager:
                #     th_manager.prm_team_id = False
                # rec.manager_id.prm_team_id = rec.id
                for member in self.th_member_ids:
                    member.write({'th_team_leader_ids': [(6, 0, self.manager_id.ids)]})

        if vals.get('th_member_ids'):
            members_ids = self.th_member_ids.ids
            members_ids.sort()
            th_flag = json.loads(self.th_flag)
            member_id = th_flag[1]
            if not member_id:
                return res
            if member_id in members_ids:
                self.th_flag = json.dumps([members_ids.index(member_id), member_id])
                return res
            if len(members_ids) == 0 or max(members_ids) < member_id:
                flag = 0
                self.th_flag = json.dumps([flag, False])
                return res
            for index, member in enumerate(members_ids):
                if member > member_id:
                    self.th_flag = json.dumps([index, member])
                    return res
        return res
