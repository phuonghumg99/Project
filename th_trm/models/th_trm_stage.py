from odoo import fields, models, api, exceptions


class ThTrmStage(models.Model):
    _name = "th.trm.stage"
    _description = "Giai đoạn"

    name = fields.Char(string="Tên giai đoạn", required=True)
    th_description = fields.Text(string='Mô tả')
    sequence = fields.Integer("Sequence")
    th_first_status = fields.Boolean(string="Trạng thái đầu")
    th_last_status = fields.Boolean(string="Trạng thái cuối" )

    @api.constrains('th_last_status')
    def _check_last_status_unique_to_type(self):
        for rec in self:
            if rec.th_last_status and self.search([('th_last_status', '=', True), ('id', '!=', rec.id)], limit=1):
                raise exceptions.ValidationError('Chỉ được có một trạng thái đầu và một trạng thái cuối')

    @api.constrains('th_first_status')
    def _check_first_status_unique_to_type(self):
        for rec in self:
            if rec.th_first_status and self.search([('th_first_status', '=', True), ('id', '!=', rec.id)], limit=1):
                raise exceptions.ValidationError('Chỉ được có một trạng thái đầu và một trạng thái cuối')

    @api.constrains('name')
    def _check_name_uniq(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name), ('id', '!=', rec.id)]) > 0:
                raise exceptions.ValidationError("Tên %s đã tồn tại." %rec.name)