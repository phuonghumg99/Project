from random import randint

from odoo import fields, models, api, exceptions


class PRMPartnerGroup(models.Model):
    _name = "prm.partner.group"
    _description = "Nhóm đối tác"

    def _get_default_color(self):
        return randint(1, 11)

    name = fields.Char(string="Tên", required=True)
    th_description = fields.Char(string="Mô tả")
    th_color = fields.Integer(string="Color", default=_get_default_color)

    @api.constrains('name')
    def _check_name_uniq(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name), ('id', '!=', rec.id)]) > 0:
                raise exceptions.ValidationError("Tên %s đã tồn tại." %rec.name)