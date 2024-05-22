from odoo import fields, models, api, exceptions


class PRMPartnerSource(models.Model):
    _name = "prm.partner.source"
    _description = "Nguồn đối tác"

    name = fields.Char(string="Tên", required=True)
    th_description = fields.Char(string="Mô tả")
    th_partner_group_id = fields.Many2one(comodel_name="prm.partner.group", string="Nhóm đối tác")

    @api.constrains('name')
    def _check_name_uniq(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name), ('id', '!=', rec.id)]) > 0:
                raise exceptions.ValidationError("Tên %s đã tồn tại." %rec.name)