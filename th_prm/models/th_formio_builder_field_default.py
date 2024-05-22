from odoo import fields, models, api, exceptions, _
import json


class FieldDefault(models.Model):
    _name = "th.formio.builder.field.default"
    _description = "Thông tin mặc định trên formio"

    th_formio_builder_id = fields.Many2one(comodel_name="formio.builder", string="Formio")
    th_default_value = fields.Char(string="", default='Giá trị mặc định', readonly=1)
    th_ownership_unit_id = fields.Many2one(comodel_name="th.ownership.unit", domain=[('th_code', '!=', 'aum')], string="Đơn vị sở hữu")
    th_partner_group_id = fields.Many2one(comodel_name="prm.partner.group", string="Nhóm đối tác")
    th_partner_source_id = fields.Many2one(comodel_name="prm.partner.source", string="Nguồn đối tác")
    th_caregiver_ids = fields.Many2many(comodel_name="res.users", string="Người chăm sóc", domain=lambda self: [('groups_id', '=', self.env.ref('th_prm.group_prm_user').id)])
    th_status_category_id = fields.Many2one(comodel_name="th.status.category", string="Tình trạng gọi")
    th_flag = fields.Char(string="Cờ")

    @api.model
    def create(self, values):
        # Add code here
        values['th_flag'] = json.dumps([0, False])
        return super(FieldDefault, self).create(values)

    def write(self, values):
        # Add code here
        res = super(FieldDefault, self).write(values)
        for rec in self:
            if values.get('th_caregiver_ids'):
                members_ids = rec.th_caregiver_ids.ids
                members_ids.sort()
                th_flag = json.loads(rec.th_flag)
                member_id = th_flag[1]
                if not member_id:
                    return res
                if member_id in members_ids:
                    rec.th_flag = json.dumps([members_ids.index(member_id), member_id])
                    return res
                if len(members_ids) == 0 or max(members_ids) < member_id:
                    flag = 0
                    rec.th_flag = json.dumps([flag, False])
                    return res
                for index, member in enumerate(members_ids):
                    if member > member_id:
                        rec.th_flag = json.dumps([index, member])
                        return res
        return res

    def action_assign_leads(self):
        for rec in self:
            member_ids = rec.th_caregiver_ids.ids
            member_ids.sort()
            th_flag = json.loads(rec.th_flag)
            flag = th_flag[0]
            result = member_ids[flag]
            flag = (flag + 1) % len(member_ids)
            rec.sudo().th_flag = json.dumps([flag, member_ids[flag]])
            return result