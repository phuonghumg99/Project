from odoo import fields, models, api, exceptions


class PRMCommissionPolicy(models.Model):
    _name = "prm.commission.policy"
    _description = "Chính sách hợp tác"

    name = fields.Char(string="Tên", required=True)
    th_description = fields.Char(string="Mô tả")

    @api.constrains('name')
    def _check_name_uniq(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name), ('id', '!=', rec.id)]) > 0:
                raise exceptions.ValidationError("Tên %s đã tồn tại." %rec.name)