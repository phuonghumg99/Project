from odoo import fields, models, api




class ThTrmSubject(models.Model):
    _name = "th.trm.subject"
    _description = "Môn học"

    name = fields.Char(string="Môn học", required=True)
    th_subject_major_ids = fields.One2many(comodel_name="th.subject.major", inverse_name="th_trm_subject_id", string="Ngành học")
    th_description = fields.Text(string='Mô tả')
    th_trm_subject_code = fields.Char(string="Mã môn")
    th_trm_subject_code_aum = fields.Char(string="Mã môn AUM")

class ThSubjectMajor(models.Model):
    _name = "th.subject.major"
    _description = "Môn - Ngành"
    _rec_name = "th_trm_major_id"

    th_subject_major_code = fields.Char(string="Mã ngành")
    th_trm_major_id = fields.Many2one(comodel_name="th.trm.major", string="Ngành học")
    th_trm_subject_id = fields.Many2one(comodel_name="th.trm.subject", string="Môn học")
    th_major_group_ids = fields.One2many(comodel_name="th.trm.group", inverse_name="th_trm_subject_major_id", string="Nhóm học", compute="_compute_th_major_group_ids")

    @api.depends('th_trm_major_id')
    def _compute_th_major_group_ids(self):
        for rec in self:
            rec.th_major_group_ids = False
            if rec.th_trm_major_id and rec.th_trm_major_id.th_major_group_ids:
                rec.th_major_group_ids = rec.th_trm_major_id.th_major_group_ids.mapped('th_trm_group_id')


class ThTrmMajor(models.Model):
    _name = "th.trm.major"
    _description = "Ngành học"

    name = fields.Char(string="Tên ngành", required=True)
    th_trm_major_code = fields.Char(string="Mã ngành AUM")
    th_description = fields.Text(string="Mô tả")
    th_trm_subject_id = fields.Many2one(comodel_name="th.trm.subject", string="Môn học")
    th_major_group_ids = fields.One2many(comodel_name="th.major.group", inverse_name="th_trm_major_id", string="Nhóm học")


class ThUniversityMajor(models.Model):
    _name = "th.major.group"
    _description = "Ngành - Nhóm"
    _rec_name = "th_trm_group_id"

    th_major_group_code = fields.Char(string="Mã nhóm")
    th_trm_group_id = fields.Many2one(comodel_name="th.trm.group", string="Nhóm học")
    th_trm_major_id = fields.Many2one(comodel_name="th.trm.major", string="Ngành học")


class ThUniversity(models.Model):
    _name = "th.trm.group"
    _description = "Nhóm học liệu"

    name = fields.Char(string="Tên nhóm", required=True)
    th_trm_major_id = fields.Many2one(comodel_name="th.trm.major", string="Ngành học")
    th_trm_group_code = fields.Char(string="Mã nhóm AUM")
    th_trm_subject_major_id = fields.Many2one(comodel_name="th.subject.major", string="Môn-Ngành")
    th_description = fields.Text(string="Mô tả")






