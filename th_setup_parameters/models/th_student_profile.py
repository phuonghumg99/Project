from odoo import fields, models, api

TH_PARTNER_ADDRESS_FIELDS_TO_SYNC = [
    'th_street',
    'th_ward_id',
    'th_district_id',
    'th_state_id',
    'th_country_id',
    'th_ethnicity_id',
    'th_religion_id',
    'th_gender',
    'th_birthday',
    'th_place_of_birth_id',
    'th_citizen_identification',
    'th_date_iden',
    'th_street_permanent',
    'th_ward_permanent_id',
    'th_district_permanent_id',
    'th_state_permanent_id',
    'th_country_permanent_id',
]
TH_VALUES_PARTNER_ADDRESS_FIELDS_TO_SYNC = {
    'th_street': 'street',
    'th_ward_id': 'th_ward_id',
    'th_district_id': 'th_district_id',
    'th_state_id': 'state_id',
    'th_country_id': 'country_id',
    'th_ethnicity_id': 'th_ethnicity_id',
    'th_religion_id': 'th_religion_id',
    'th_gender': 'th_gender',
    'th_birthday': 'th_birthday',
    'th_place_of_birth_id': 'th_place_of_birth_id',
    'th_citizen_identification': 'th_citizen_identification',
    'th_date_iden': 'th_date_identification',
    'th_street_permanent': 'th_street',
    'th_ward_permanent_id': 'th_ward_permanent_id',
    'th_district_permanent_id': 'th_district_permanent_id',
    'th_state_permanent_id': 'th_state_id',
    'th_country_permanent_id': 'th_country_id',
}

class ThStudentProfile(models.Model):
    _name = "th.student.profile"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Hồ sơ sinh viên"

    def _th_domain_place_of_birth(self):
        state_id = self.env['res.country.state'].search([]).filtered(lambda u: u.country_id == self.env.ref('base.vn'))
        return [('id', 'in', state_id.ids)]

    name = fields.Char(string="Hồ sơ", compute="_compute_partner_address_values")
    th_partner_id = fields.Many2one(comodel_name="res.partner", string="Hồ sơ của", index=True)
    th_first_and_last_name = fields.Char(string="Họ và tên", compute="_compute_partner_address_values", inverse='_inverse_th_first_and_last_name',store=False)
    th_date_of_delivery = fields.Date(string="Ngày bàn giao trường")
    th_check_date_of_delivery = fields.Boolean()
    th_date_of_receipt = fields.Date(string="Ngày nhận HS-TVTS")
    th_handover_status = fields.Selection(selection=[('not_handed', 'Chưa bàn giao'), ('handed_over', 'Đã bàn giao')], string="Tình trạng bàn giao", default='not_handed')
    th_reason = fields.Text(string="Lý do")

    th_profile_status = fields.Selection(selection=[('full', 'Đủ'), ('missing', 'Thiếu')], string="Tình trạng hồ sơ")
    th_cover_profile = fields.Char(string="Vỏ")
    th_profile_image = fields.Char(string="Ảnh")
    th_profile_degree = fields.Char(string="Bằng")
    th_profile_graduate = fields.Char(string="Chứng nhận tốt nghiệp")
    th_profile_transcript = fields.Char(string="Bảng điểm")
    th_school_profile = fields.Char(string="Học bạ")
    th_pdk = fields.Char(string="Phiếu đăng ký")
    th_test_paper = fields.Char(string="Giấy khảo sát")
    th_citizen_identification = fields.Char(string="CMT/ CCCD", compute="_compute_partner_address_values", inverse='_inverse_th_citizen_identification',store=False)
    th_curriculum_vitae = fields.Char(string="Sơ yếu lý lịch")
    th_score_transfer = fields.Char(string="Phiếu chuyển điểm kết quả học tập")
    th_other = fields.Char(string="Khác")
    th_combination_sub_id = fields.Many2one(comodel_name="th.combination.subjects", string="Tổ hợp môn")
    th_subject_score_1 = fields.Float(string="Điểm lớp 12. Môn 1")
    th_subject_score_2 = fields.Float(string="Điểm lớp 12. Môn 2")
    th_subject_score_3 = fields.Float(string="Điểm lớp 12. Môn 3")
    th_medium_score_in4 = fields.Float(string="Điểm TBC TL/Học tập.Thang 4", compute="_computeth_medium_score_in4", inverse="_set_th_medium_score_in10")
    th_medium_score_in10 = fields.Float(string="Điểm TBC TL/Học tập.Thang 10")
    th_graduation_rank = fields.Char(string="Hạng tốt nghiệp")
    th_unit_for_work = fields.Char(string="Đơn vị công tác")
    th_awarding_diplomas = fields.Char(string="Nơi trao bằng tốt nghiệp")
    th_major_studied = fields.Char(string="Chuyên ngành đã học")
    th_high_school = fields.Char(string="Trường THPT")
    th_graduation_year = fields.Char(string="Năm tốt nghiệp")
    th_form_of_train = fields.Char(string="Hình thức đào tạo")
    th_certificate_number = fields.Char(string="Số hiệu bằng")
    th_reference_number = fields.Char(string="Số vào sổ")
    th_job = fields.Char(string="Nghề nghiệp")
    th_reusable_source_name = fields.Char(string="Tên nguồn tái sử dụng")
    th_date_iden = fields.Date(string="Ngày cấp CMT/ CCCD", compute="_compute_partner_address_values", inverse='_inverse_th_date_iden', store=False)

    th_street = fields.Char('Địa chỉ', compute="_compute_partner_address_values", inverse='_inverse_th_street',store=False)
    th_ward_id = fields.Many2one(comodel_name='th.country.ward', string='Phường/ Xã', domain="[('th_district_id', '=?', th_district_id), ('th_district_id.th_state_id', '=?', th_state_id)]",
                                 compute="_compute_partner_address_values", inverse='_inverse_th_ward_id',store=False)
    th_district_id = fields.Many2one(comodel_name='th.country.district', string='Quận/ Huyện', domain="[('th_state_id', '=?', th_state_id)]",
                                     compute="_compute_partner_address_values", inverse='_inverse_th_district_id',store=False)
    th_state_id = fields.Many2one(comodel_name="res.country.state", string='Tỉnh/ Thành phố', domain="[('country_id', '=?', th_country_id)]",
                                  compute="_compute_partner_address_values", inverse='_inverse_th_state_id',store=False)
    th_country_id = fields.Many2one(comodel_name='res.country', string='Quốc Gia', default=lambda x: x.env.ref('base.vn'),
                                    compute="_compute_partner_address_values", inverse='_inverse_th_country_id',store=False)

    th_street_permanent = fields.Char(tracking=True, string="Địa chỉ (Hộ khẩu)",
                                      compute="_compute_partner_address_values", inverse='_inverse_th_street_permanent',
                                      store=False)

    th_ward_permanent_id = fields.Many2one(comodel_name='th.country.ward', string='Phường/ Xã (Hộ khẩu)',
                                           domain="[('th_district_id', '=?', th_district_permanent_id), ('th_district_id.th_state_id', '=?', th_state_id)]",
                                           tracking=True, compute="_compute_partner_address_values",
                                           inverse='_inverse_th_ward_permanent_id', store=False)
    th_district_permanent_id = fields.Many2one(comodel_name='th.country.district', string='Quận/ Huyện (Hộ khẩu)',
                                               domain="[('th_state_id', '=?', th_state_id)]", tracking=True,
                                               compute="_compute_partner_address_values",
                                               inverse='_inverse_th_district_permanent_id', store=False)
    th_state_permanent_id = fields.Many2one("res.country.state", string='Tỉnh/ TP (Hộ khẩu)',
                                            domain="[('country_id', '=?', th_country_id)]", tracking=True,
                                            compute="_compute_partner_address_values",
                                            inverse='_inverse_th_state_permanent_id', store=False)
    th_country_permanent_id = fields.Many2one('res.country', string='Quốc gia (Hộ khẩu)',
                                              tracking=True,
                                              compute="_compute_partner_address_values",
                                              inverse='_inverse_th_country_permanent_id', store=False)



    th_ethnicity_id = fields.Many2one(comodel_name="th.ethnicity", string="Dân tộc", compute="_compute_partner_address_values", inverse='_inverse_th_ethnicity_id',store=False)
    th_religion_id = fields.Many2one(comodel_name="th.religion", string="Tôn giáo", compute="_compute_partner_address_values", inverse='_inverse_th_religion_id',store=False)
    th_gender = fields.Selection(string="Giới tính", selection=[('male', 'Nam'), ('female', 'Nữ'), ('other', 'Khác'), ], compute="_compute_partner_address_values", inverse='_inverse_th_gender',store=False)
    th_birthday = fields.Date(string="Ngày sinh", compute="_compute_partner_address_values", inverse='_inverse_th_birthday',store=False)
    th_place_of_birth_id = fields.Many2one(comodel_name="res.country.state", string="Nơi sinh", domain=_th_domain_place_of_birth, compute="_compute_partner_address_values", inverse='_inverse_th_place_of_birth_id',store=False)

    th_father_name = fields.Char(string="Họ tên cha")
    th_father_job = fields.Char(string="Nghề nghiệp cha")
    th_father_birther = fields.Char(string="Ngày sinh cha")

    th_mother_name = fields.Char(string="Họ tên mẹ")
    th_mother_job = fields.Char(string="Nghề nghiệp mẹ")
    th_mother_birther = fields.Char(string="Ngày sinh mẹ")

    # th_university_id = fields.Many2one(comodel_name="th.university", string="Trường")
    th_origin_id = fields.Many2one(comodel_name="th.origin", string="Trường")
    th_decision_name = fields.Char(string="Tên quyết định trúng tuyển")
    th_decision_date = fields.Date(string="Ngày có quyết định trúng tuyển")
    th_student_code = fields.Char('Mã sinh viên')
    def action_view_crm_lead(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Cơ hội CRM',
            'view_mode': 'tree,form',
            'res_model': 'crm.lead',
            'target': 'current',
            'domain': [('id', '=', self.th_lead_id.id)],
            'context': {'create': False}
        }

    def _prepare_address_values_from_partner(self, partner):
        # Sync all address fields from partner, or none, to avoid mixing them.
        if any(partner[TH_VALUES_PARTNER_ADDRESS_FIELDS_TO_SYNC.get(f)] for f in TH_PARTNER_ADDRESS_FIELDS_TO_SYNC):
            values = {f: partner[TH_VALUES_PARTNER_ADDRESS_FIELDS_TO_SYNC.get(f)] for f in TH_PARTNER_ADDRESS_FIELDS_TO_SYNC}
        else:
            values = {f: self[f] for f in TH_PARTNER_ADDRESS_FIELDS_TO_SYNC}
        return values

    @api.depends('th_partner_id')
    def _compute_partner_address_values(self):
        """ Sync all or none of address fields """
        for lead in self:
            lead.name = f"Hồ sơ {lead.th_partner_id.name}" if lead.th_partner_id else False
            lead.th_first_and_last_name = lead.th_partner_id.name if lead.th_partner_id else False
            lead.update(lead._prepare_address_values_from_partner(lead.th_partner_id))

    def _inverse_th_street_permanent(self):
        for rec in self:
            if rec.th_street_permanent:
                rec.th_partner_id.th_street = rec.th_street_permanent

    def _inverse_th_ward_permanent_id(self):
        for rec in self:
            if rec.th_ward_permanent_id:
                rec.th_partner_id.th_ward_permanent_id = rec.th_ward_permanent_id.id

    def _inverse_th_district_permanent_id(self):
        for rec in self:
            if rec.th_district_permanent_id:
                rec.th_partner_id.th_district_permanent_id = rec.th_district_permanent_id.id

    def _inverse_th_state_permanent_id(self):
        for rec in self:
            if rec.th_state_permanent_id:
                rec.th_partner_id.th_state_id = rec.th_state_permanent_id.id

    def _inverse_th_country_permanent_id(self):
        for rec in self:
            if rec.th_country_permanent_id:
                rec.th_partner_id.th_country_id = rec.th_country_permanent_id.id
    def _inverse_th_street(self):
        for rec in self:
            rec.th_partner_id.street = rec.th_street

    def _inverse_th_ward_id(self):
        for rec in self:
            rec.th_partner_id.th_ward_id = rec.th_ward_id.id

    def _inverse_th_district_id(self):
        for rec in self:
            rec.th_partner_id.th_district_id = rec.th_district_id.id

    def _inverse_th_state_id(self):
        for rec in self:
            rec.th_partner_id.state_id = rec.th_state_id.id

    def _inverse_th_country_id(self):
        for rec in self:
            rec.th_partner_id.country_id = rec.th_country_id.id

    def _inverse_th_ethnicity_id(self):
        for rec in self:
            rec.th_partner_id.th_ethnicity_id = rec.th_ethnicity_id.id

    def _inverse_th_religion_id(self):
        for rec in self:
            rec.th_partner_id.th_religion_id = rec.th_religion_id.id

    def _inverse_th_gender(self):
        for rec in self:
            rec.th_partner_id.th_gender = rec.th_gender

    def _inverse_th_birthday(self):
        for rec in self:
            rec.th_partner_id.th_birthday = rec.th_birthday

    def _inverse_th_place_of_birth_id(self):
        for rec in self:
            rec.th_partner_id.th_place_of_birth_id = rec.th_place_of_birth_id.id

    def _inverse_th_first_and_last_name(self):
        for rec in self:
            rec.th_partner_id.name = rec.th_first_and_last_name

    def _inverse_th_citizen_identification(self):
        for rec in self:
            rec.th_partner_id.th_citizen_identification = rec.th_citizen_identification

    def _inverse_th_date_iden(self):
        for rec in self:
            rec.th_partner_id.th_date_identification = rec.th_date_iden

    @api.onchange('th_ward_id')
    def onchange_th_ward_id(self):
        if self.th_ward_id:
            self.th_district_id = self.th_ward_id.th_district_id.id
            self.th_state_id = self.th_district_id.th_state_id.id
            self.th_country_id = self.th_state_id.country_id.id

    @api.onchange('th_district_id')
    def onchange_th_district_id(self):
        if self.th_district_id:
            self.th_state_id = self.th_district_id.th_state_id.id
            self.th_country_id = self.th_state_id.country_id.id
        if self.th_district_id != self.th_ward_id.th_district_id:
            self.th_ward_id = False

    @api.onchange('th_state_id')
    def onchange_th_state_id(self):
        if self.th_state_id:
            self.th_country_id = self.th_state_id.country_id.id
        if self.th_state_id != self.th_district_id.th_state_id:
            self.th_district_id = False

    @api.onchange('th_ward_permanent_id')
    def onchange_th_ward_permanent_id(self):
        if self.th_ward_permanent_id:
            self.th_district_permanent_id = self.th_ward_permanent_id.th_district_id.id
            self.th_state_permanent_id = self.th_district_permanent_id.th_state_id.id
            self.th_country_permanent_id = self.th_state_permanent_id.country_id.id

    @api.onchange('th_district_permanent_id')
    def onchange_th_district_permanent_id(self):
        if self.th_district_permanent_id:
            self.th_state_permanent_id = self.th_district_permanent_id.th_state_id.id
            self.th_country_permanent_id = self.th_state_permanent_id.country_id.id
        if self.th_district_permanent_id != self.th_ward_permanent_id.th_district_id:
            self.th_ward_permanent_id = False

    @api.onchange('th_country_permanent_id')
    def onchange_th_country_permanent_id(self):
        if self.th_country_permanent_id != self.th_state_permanent_id.country_id:
            self.th_state_permanent_id = False

    @api.onchange('th_state_permanent_id')
    def onchange_th_state_permanent_id(self):
        if self.th_state_permanent_id:
            self.th_country_permanent_id = self.th_state_permanent_id.country_id.id
        if self.th_state_permanent_id != self.th_district_permanent_id.th_state_id:
            self.th_district_permanent_id = False

    @api.onchange('th_country_id')
    def onchange_th_country_id(self):
        if self.th_country_id != self.th_state_id.country_id:
            self.th_state_id = False

    @api.depends('th_medium_score_in10')
    def _computeth_medium_score_in4(self):
        for rec in self:
            rec.th_medium_score_in4 = rec.th_medium_score_in10/2.5 if rec.th_medium_score_in10 else False

    def _set_th_medium_score_in10(self):
        for rec in self:
            rec.th_medium_score_in10 = rec.th_medium_score_in4 * 2.5 if rec.th_medium_score_in4 else False

    def _prepare_address_values_from_partner(self, partner):
        # Sync all address fields from partner, or none, to avoid mixing them.
        if any(partner[TH_VALUES_PARTNER_ADDRESS_FIELDS_TO_SYNC.get(f)] for f in TH_PARTNER_ADDRESS_FIELDS_TO_SYNC):
            values = {f: partner[TH_VALUES_PARTNER_ADDRESS_FIELDS_TO_SYNC.get(f)] for f in TH_PARTNER_ADDRESS_FIELDS_TO_SYNC}
        else:
            values = {f: self[f] for f in TH_PARTNER_ADDRESS_FIELDS_TO_SYNC}
        return values

    @api.depends('th_partner_id')
    def _compute_partner_address_values(self):
        """ Sync all or none of address fields """
        for lead in self:
            lead.name = f"Hồ sơ {lead.th_partner_id.name}" if lead.th_partner_id else False
            lead.th_first_and_last_name = lead.th_partner_id.name if lead.th_partner_id else False
            lead.update(lead._prepare_address_values_from_partner(lead.th_partner_id))


    def _inverse_th_ethnicity_id(self):
        for rec in self:
            rec.th_partner_id.th_ethnicity_id = rec.th_ethnicity_id.id

    def _inverse_th_religion_id(self):
        for rec in self:
            rec.th_partner_id.th_religion_id = rec.th_religion_id.id

    def _inverse_th_gender(self):
        for rec in self:
            rec.th_partner_id.th_gender = rec.th_gender

    def _inverse_th_birthday(self):
        for rec in self:
            rec.th_partner_id.th_birthday = rec.th_birthday

    def _inverse_th_place_of_birth_id(self):
        for rec in self:
            rec.th_partner_id.th_place_of_birth_id = rec.th_place_of_birth_id.id

    def _inverse_th_first_and_last_name(self):
        for rec in self:
            rec.th_partner_id.name = rec.th_first_and_last_name

    def _inverse_th_citizen_identification(self):
        for rec in self:
            rec.th_partner_id.th_citizen_identification = rec.th_citizen_identification

    def _inverse_th_date_iden(self):
        for rec in self:
            rec.th_partner_id.th_date_identification = rec.th_date_iden


