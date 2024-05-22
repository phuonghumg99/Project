from odoo import fields, models, api, exceptions

class PRMLevel(models.Model):
    _name = "prm.level"
    _description = "Mối quan hệ"
    _rec_name = "name"
    _order = 'th_sequence asc'

    name = fields.Char(string="Tên", required=True)
    th_type = fields.Selection(string="Loại", selection=[('prm', 'PRM'), ('pom', 'POM')], required=True, default="prm")
    th_sequence = fields.Integer(string="", default=1)
    th_last_status = fields.Boolean(string="Trạng thái cuối")
    th_first_status = fields.Boolean(string="Trạng thái đầu")
    th_description = fields.Char(string="Mô tả")

    @api.constrains('th_last_status')
    def _check_last_status_unique_to_type(self):
        for rec in self:
            if rec.th_last_status and self.search([('th_type', '=', rec.th_type), ('th_last_status', '=', True), ('id', '!=', rec.id)], limit=1):
                raise exceptions.ValidationError('Mỗi loại chỉ được có một trạng thái cuối')

    @api.constrains('th_first_status')
    def _check_first_status_unique_to_type(self):
        for rec in self:
            if rec.th_first_status and self.search(
                    [('th_type', '=', rec.th_type), ('th_first_status', '=', True), ('id', '!=', rec.id)], limit=1):
                raise exceptions.ValidationError('Mỗi loại chỉ được có một trạng thái đầu')

    @api.constrains('name')
    def _check_name_uniq(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name), ('id', '!=', rec.id)]) > 0:
                raise exceptions.ValidationError("Tên %s đã tồn tại." %rec.name)

    # @api.ondelete(at_uninstall=False)
    # def _unlink_prm_level_record(self):
    #     if not self.th_is_delete:
    #         raise exceptions.UserError('Không thể xóa bản ghi này, vui lòng liên hệ nhà phát triển')
