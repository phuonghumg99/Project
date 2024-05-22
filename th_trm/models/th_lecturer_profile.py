from odoo import api, fields, models
from odoo.exceptions import ValidationError


class ThLecturerProfile(models.Model):
    _name = "th.lecturer.profile"
    _description = "Hồ sơ giảng viên"
    _inherit = 'mail.thread'

    def _domain_th_subjects_taught(self):
        return [('categ_id', 'in', self.env['product.category'].search([]).filtered(lambda lam: self.env.ref('th_setup_parameters.th_trm_module').id in lam.th_module_ids.ids).ids)]

    name = fields.Char(string="Tên hồ sơ", tracking=True, compute="_compute_name_profile", store=True)
    th_partner_id = fields.Many2one(comodel_name="res.partner", string="Tên giảng viên", index=True, tracking=True)
    th_customer_code = fields.Char(string='Mã giảng viên', related="th_partner_id.th_customer_code", readonly=True,
                                   tracking=True)
    th_getfly_code = fields.Char(string="Mã KH getfly")
    th_affiliate_code = fields.Char(string='Mã tiếp thị liên kết', related="th_partner_id.th_affiliate_code",
                                    tracking=True)
    th_date_of_delivery = fields.Date(string="Ngày bàn giao", tracking=True)
    th_date_of_receipt = fields.Date(string="Ngày nhận Hồ Sơ", tracking=True)
    th_handover_status = fields.Selection(
        selection=[('wfhandover', 'Chờ bàn giao'), ('not_handed', 'Chưa bàn giao'), ('handed_over', 'Đã bàn giao')],
        string="Tình trạng bàn giao", tracking=True)
    th_reason = fields.Text(string="Lý do", tracking=True)
    th_trm_other = fields.Text(string="Khác", tracking=True)
    th_profile_file = fields.Many2many("ir.attachment", string="Tệp đính kèm", tracking=True)
    th_legal_records = fields.Selection([('pass', 'Đạt'), ('fail', 'Không đạt')], string="Hồ sơ pháp lý", tracking=True)

    th_profile_status = fields.Selection(
        selection=[('full', 'Đủ'), ('hard_collect', 'Khó thu'), ('continue_collect', 'Tiếp tục thu')],
        string="Tình trạng Hồ Sơ", tracking=True)
    th_street = fields.Char('Địa chỉ', inverse='_inverse_th_street', compute="_compute_partner_values",
                            tracking=True, store=True)
    th_ward_id = fields.Many2one(comodel_name='th.country.ward', string='Phường/ Xã',
                                 compute="_compute_partner_values", inverse='_inverse_th_ward_id',
                                 domain="[('th_district_id', '=?', th_district_id), ('th_district_id.th_state_id', '=?', th_state_id)]",
                                 tracking=True, store=True)
    th_district_id = fields.Many2one(comodel_name='th.country.district', string='Quận/ Huyện',
                                     compute="_compute_partner_values", inverse='_inverse_th_district_id',
                                     domain="[('th_state_id', '=?', th_state_id)]", tracking=True, store=True)
    th_state_id = fields.Many2one(comodel_name="res.country.state", string='Tỉnh/ Thành phố',
                                  compute="_compute_partner_values", inverse='_inverse_th_state_id',
                                  domain="[('country_id', '=?', th_country_id)]", tracking=True, store=True)
    th_country_id = fields.Many2one(comodel_name='res.country', string='Quốc Gia',
                                    compute="_compute_partner_values", inverse='_inverse_th_country_id',
                                    default=lambda x: x.env.ref('base.vn'), tracking=True)
    th_street_workplace = fields.Char('Địa chỉ làm việc', tracking=True)
    th_ward_workplace = fields.Many2one(comodel_name='th.country.ward', string='Phường/ Xã',
                                        domain="[('th_district_id', '=?', th_district_workplace), ('th_district_id.th_state_id', '=?', th_state_workplace_id)]",
                                        tracking=True, store=True)
    th_district_workplace = fields.Many2one(comodel_name='th.country.district', string='Quận/ Huyện',
                                            domain="[('th_state_id', '=?', th_state_workplace_id)]",
                                            tracking=True, store=True)
    th_state_workplace_id = fields.Many2one(comodel_name="res.country.state", string='Tỉnh/ Thành phố',
                                            domain="[('country_id', '=?', th_country_id)]", tracking=True, store=True)
    th_country_workplace_id = fields.Many2one(comodel_name='res.country', string='Quốc Gia',
                                              default=lambda x: x.env.ref('base.vn'), tracking=True)
    th_ethnicity_id = fields.Many2one(comodel_name="th.ethnicity", string="Dân tộc", store=True,
                                      compute="_compute_partner_values", inverse='_inverse_th_ethnicity_id',
                                      tracking=True)
    th_religion_id = fields.Many2one(comodel_name="th.religion", string="Tôn giáo", store=True,
                                     compute="_compute_partner_values", inverse='_inverse_th_religion_id',
                                     tracking=True)
    th_gender = fields.Selection(string="Giới tính", selection=[('male', 'Nam'), ('female', 'Nữ'), ('other', 'Khác'), ],
                                 compute="_compute_partner_values", inverse='_inverse_th_gender', tracking=True,
                                 store=True)
    th_birthday = fields.Date(string="Ngày sinh", inverse='_inverse_th_birthday',
                              compute="_compute_partner_values", tracking=True)
    th_citizen_identification = fields.Char(string="CMT/ CCCD", inverse='_inverse_th_citizen_identification',
                                            compute="_compute_partner_values",
                                            tracking=True, store=True)
    th_date_identification = fields.Date(string="Ngày cấp CMT/ CCCD", inverse='_inverse_th_date_identification',
                                         compute="_compute_partner_values", tracking=True)
    th_place_identification = fields.Char(string="Nơi cấp CMT/ CCCD", inverse='_inverse_th_place_identification',
                                          compute="_compute_partner_values", tracking=True)
    th_citizen_identification_image = fields.Binary(string="Ảnh CMT/ CCCD")
    th_citizen_identification_image_filename = fields.Char(string="Tên file ảnh căn cước công dân")
    th_place_of_birth_id = fields.Many2one(comodel_name="res.country.state", string="Nơi sinh",
                                           compute="_compute_partner_values",
                                           inverse='_inverse_th_place_of_birth_id',
                                           tracking=True)
    th_trm_phone = fields.Char(string="Điện thoại", tracking=True, inverse='_inverse_th_trm_phone',
                               compute='_compute_partner_values')
    th_trm_phone2 = fields.Char(string="Điện thoại 2", tracking=True, inverse='_inverse_th_trm_phone2',
                                compute='_compute_partner_values', readonly=False)
    th_trm_email = fields.Char(string="Email", inverse='_inverse_th_trm_email',
                               compute='_compute_partner_values', tracking=True)

    th_trm_certificate = fields.Text(string="Chứng chỉ", tracking=True)
    th_trm_certificate1 = fields.Text(string="Chứng chỉ", tracking=True)
    th_trm_qualifications = fields.Text(string="Bằng cấp", tracking=True)
    th_trm_qualifications1 = fields.Text(string="Bằng cấp", tracking=True)
    th_graduation_rank = fields.Char(string="Hạng tốt nghiệp", tracking=True)
    th_unit_for_work = fields.Text(string="Đơn vị công tác", tracking=True)
    th_major_studied = fields.Char(string="Chuyên ngành đã học", tracking=True)
    th_graduation_year = fields.Char(string="Năm tốt nghiệp", tracking=True)
    th_form_of_train = fields.Char(string="Hình thức đào tạo", tracking=True)
    th_certificate_number = fields.Char(string="Số hiệu bằng", tracking=True)
    th_lecturers_code = fields.Selection(
        [('V07.01.01', 'V07.01.01'), ('V07.01.02', 'V07.01.02'), ('V07.01.03', 'V07.01.03'), ('15.109', '15.109'),
         ('15.110', '15.110'), ('15.111', '15.111')], string="Mã ngạch giảng viên", tracking=True)
    th_meet_certificate = fields.Selection([('pass', 'Đạt'), ('fail', 'Không đạt')], string="Mức đáp ứng chứng chỉ",
                                           tracking=True)

    th_bank_ids = fields.One2many('res.partner.bank', 'th_lecturer_profile_id', string='Ngân hàng')
    th_tax_no = fields.Char(string="Mã số thuế", compute="_compute_partner_values", inverse='_inverse_th_tax_no',
                            tracking=True, store=True)
    th_contract_number = fields.Char(string="Số hợp đồng", tracking=True)
    th_contract_sign_date = fields.Text(string="Ngày ký hợp đồng", tracking=True)

    th_voice = fields.Text(string="Giọng nói", tracking=True)
    th_appearance = fields.Text(string="Ngoại hình", tracking=True)
    th_charisma = fields.Text(string="Thần thái", tracking=True)
    th_pedagogical_ability = fields.Text(string="Khả năng sư phạm", tracking=True)
    th_famous = fields.Text(string="Nổi tiếng", tracking=True)
    th_moral_qualities = fields.Text(string="Phẩm chất đạo đức", tracking=True)
    th_experience = fields.Text(string="Kinh nghiệm", tracking=True)
    th_skill = fields.Text(string="Kỹ năng", tracking=True)
    activity_ids = fields.One2many('mail.activity', 'calendar_event_id', string='Activities')
    th_lead_id = fields.Many2one(comodel_name="th.trm.lead", string="Cơ hội sản xuất", tracking=True)
    th_quantity = fields.Integer(compute="_compute_th_quantity")
    th_subjects_taught = fields.Many2many(comodel_name="product.template", string="Lĩnh vực giảng dạy", domain=_domain_th_subjects_taught)

    @api.model
    def create(self, vals_list):
        res = super().create(vals_list)
        for rec in res:
            if self._context.get('import_file'):
                partner = self.env['res.partner'].search([('th_customer_code', '=', rec.th_getfly_code)])
                if not partner:
                    raise ValidationError(f"Không tìm thấy giảng viên với mã KH: {rec.th_getfly_code}")
                rec.write({'th_partner_id': partner})

        return res

    def action_create_trm_lead(self):
        self.ensure_one()
        return {
            'name': 'Cơ hội sản xuất',
            'view_mode': 'form',
            'res_model': 'th.trm.lead',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {
                        'default_th_partner_id': self.id,
                        'readonly_th_partner_id': True,
                        'invisible_button': True,
                        },
        }

    @api.constrains('th_partner_id')
    def _check_duplicate_values(self):
        for rec in self:
            domain = [('id', '!=', rec.id),
                      ('th_partner_id', '=', rec.th_partner_id.id), ('th_partner_id', '!=', False),
                      ('th_trm_phone', '=', rec.th_trm_phone), ('th_trm_phone', '!=', False),
                      ('th_trm_email', '=', rec.th_trm_email), ('th_trm_email', '!=', False),
                      ]
            if self.search(domain):
                raise ValidationError("Trùng hồ sơ!")

    def action_open_registered_subject(self):
        self.ensure_one()
        return {
            'name': 'Cơ hội sản xuất',
            'view_mode': 'tree',
            'res_model': 'th.trm.lead',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': [('th_partner_id', '=', self.id)],
            'context': {'create': False,
                        },
        }

    def _compute_th_quantity(self):
        for rec in self:
            rec.th_quantity = len(self.env['th.trm.lead'].search([('th_partner_id', '=', self.id)]))

    @api.depends('th_partner_id')
    def _compute_name_profile(self):
        for rec in self:
            rec.name = rec.th_partner_id.name if rec.th_partner_id else 'Mới'

    @api.depends('th_partner_id')
    def _compute_partner_values(self):
        for rec in self:
            if not rec.th_partner_id:
                return False
            rec.th_trm_phone = rec.th_partner_id.phone
            rec.th_trm_phone2 = rec.th_partner_id.th_phone2
            rec.th_trm_email = rec.th_partner_id.email
            rec.th_street = rec.th_partner_id.street
            rec.th_tax_no = rec.th_partner_id.vat
            rec.th_ward_id = rec.th_partner_id.th_ward_id
            rec.th_state_id = rec.th_partner_id.state_id
            rec.th_country_id = rec.th_partner_id.country_id
            rec.th_ethnicity_id = rec.th_partner_id.th_ethnicity_id
            rec.th_religion_id = rec.th_partner_id.th_religion_id
            rec.th_place_of_birth_id = rec.th_partner_id.th_place_of_birth_id
            rec.th_citizen_identification = rec.th_partner_id.th_citizen_identification
            rec.th_date_identification = rec.th_partner_id.th_date_identification
            rec.th_place_identification = rec.th_partner_id.th_place_identification
            rec.th_birthday = rec.th_partner_id.th_birthday
            rec.th_gender = rec.th_partner_id.th_gender
            rec.th_district_id = rec.th_partner_id.th_district_id

    def _inverse_th_street(self):
        for rec in self:
            rec.th_partner_id.street = rec.th_street

    def _inverse_th_district_id(self):
        for rec in self:
            rec.th_partner_id.th_district_id = rec.th_district_id.id

    def _inverse_th_ward_id(self):
        for rec in self:
            rec.th_partner_id.th_ward_id = rec.th_ward_id.id

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

    def _inverse_th_citizen_identification(self):
        for rec in self:
            rec.th_partner_id.th_citizen_identification = rec.th_citizen_identification

    def _inverse_th_date_identification(self):
        for rec in self:
            rec.th_partner_id.th_date_identification = rec.th_date_identification

    def _inverse_th_place_identification(self):
        for rec in self:
            rec.th_partner_id.th_place_identification = rec.th_place_identification

    def _inverse_th_trm_phone(self):
        for rec in self:
            if not rec.th_partner_id: return
            rec.th_partner_id.phone = rec.th_trm_phone

    def _inverse_th_trm_phone2(self):
        for rec in self:
            if not rec.th_partner_id: return
            rec.th_partner_id.th_phone2 = rec.th_trm_phone2

    def _inverse_th_trm_email(self):
        for rec in self:
            if not rec.th_partner_id: return
            rec.th_partner_id.email = rec.th_trm_email

    def _inverse_th_tax_no(self):
        for rec in self:
            if not rec.th_partner_id: return
            rec.th_partner_id.vat = rec.th_tax_no
