from odoo import fields, models, api


class ResUsers(models.Model):
    _inherit = "res.users"

    th_trm_team_id = fields.Many2one(comodel_name="th.trm.team", string="Đội học liệu", store=True)
    th_team_leader_ids = fields.Many2many(comodel_name="res.users",relation="th_leader_ref", column1="th_user", column2="th_leader", string="Đội trưởng", store=True)
