from odoo import fields, models, exceptions, api


class PRMReasonQuit(models.Model):
    _name = "prm.reason.quit"
    _description = "Lý do ngừng hợp tác"

    name = fields.Char(string="Loại", required=True)
    th_reason_quit_detail_ids = fields.One2many(comodel_name="prm.reason.quit.detail", inverse_name="th_reason_quit_id", string="Chi tiết")

    @api.constrains('name')
    def _check_name_uniq(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name), ('id', '!=', rec.id)]) > 0:
                raise exceptions.ValidationError("Tên %s đã tồn tại." %rec.name)
