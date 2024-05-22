from odoo import api, fields, models, tools


class ThPartnerProfile(models.Model):
    _name = "th.partner.profile"
    _description = "Hồ sơ đối tác"
    _inherit = 'mail.thread'

    name = fields.Char(string="Tên hồ sơ", tracking=True, compute="_compute_name_profile", store=True)
    th_partner_id = fields.Many2one(comodel_name="res.partner", string="Tên đối tác", index=True, tracking=True)
    th_customer_code = fields.Char(string='Mã đối tác', related="th_partner_id.th_customer_code", readonly=True,
                                   tracking=True)
    th_affiliate_code = fields.Char(string='Mã tiếp thị liên kết', related="th_partner_id.th_affiliate_code",
                                    tracking=True)
    th_description = fields.Text(string="Mô tả", tracking=True)
    th_curriculum_vitae = fields.Char(string="Sơ yếu lí lịch", tracking=True)
    th_street = fields.Char('Địa chỉ', inverse='_inverse_th_street', compute="_compute_partner_values",
                            tracking=True)
    th_ward_id = fields.Many2one(comodel_name='th.country.ward', string='Phường/ Xã',
                                 compute="_compute_partner_values", inverse='_inverse_th_ward_id',
                                 domain="[('th_district_id', '=?', th_district_id), ('th_district_id.th_state_id', '=?', th_state_id)]",
                                 tracking=True)
    th_district_id = fields.Many2one(comodel_name='th.country.district', string='Quận/ Huyện',
                                     compute="_compute_partner_values", inverse='_inverse_th_district_id',
                                     domain="[('th_state_id', '=?', th_state_id)]", tracking=True)
    th_state_id = fields.Many2one(comodel_name="res.country.state", string='Tỉnh/ Thành phố',
                                  compute="_compute_partner_values", inverse='_inverse_th_state_id',
                                  domain="[('country_id', '=?', th_country_id)]", tracking=True)
    th_country_id = fields.Many2one(comodel_name='res.country', string='Quốc Gia',
                                    compute="_compute_partner_values", inverse='_inverse_th_country_id',
                                    default=lambda x: x.env.ref('base.vn'), tracking=True)
    th_ethnicity_id = fields.Many2one(comodel_name="th.ethnicity", string="Dân tộc",
                                      compute="_compute_partner_values", inverse='_inverse_th_ethnicity_id',
                                      tracking=True)
    th_religion_id = fields.Many2one(comodel_name="th.religion", string="Tôn giáo",
                                     compute="_compute_partner_values", inverse='_inverse_th_religion_id',
                                     tracking=True)
    th_gender = fields.Selection(string="Giới tính", selection=[('male', 'Nam'), ('female', 'Nữ'), ('other', 'Khác'), ],
                                 compute="_compute_partner_values", inverse='_inverse_th_gender', tracking=True)
    th_birthday = fields.Date(string="Ngày sinh", inverse='_inverse_th_birthday',
                              compute="_compute_partner_values", tracking=True)
    th_citizen_identification = fields.Char(string="CMT/ CCCD", inverse='_inverse_th_citizen_identification',
                                            compute="_compute_partner_values",
                                            tracking=True)
    th_date_identification = fields.Date(string="Ngày cấp CMT/ CCCD", inverse='_inverse_th_date_identification',
                                         compute="_compute_partner_values", tracking=True)
    th_place_identification = fields.Char(string="Nơi cấp CMT/ CCCD", inverse='_inverse_th_place_identification',
                                          compute="_compute_partner_values", tracking=True)
    th_place_of_birth_id = fields.Many2one(comodel_name="res.country.state", string="Nơi sinh",
                                           compute="_compute_partner_values",
                                           inverse='_inverse_th_place_of_birth_id',
                                           tracking=True)
    th_citizen_identification_image = fields.Binary(string="Ảnh căn cước công dân")
    th_citizen_identification_image_filename = fields.Char(string="Tên file ảnh căn cước công dân")

    th_prm_phone = fields.Char(string="Điện thoại", tracking=True, inverse='_inverse_th_prm_phone',
                               compute='_compute_partner_values')
    th_prm_phone2 = fields.Char(string="Điện thoại 2", tracking=True, inverse='_inverse_th_prm_phone2',
                                compute='_compute_partner_values', readonly=False)
    th_prm_email = fields.Char(string="Email", inverse='_inverse_th_prm_email',
                               compute='_compute_partner_values', tracking=True)
    th_quantity_prm = fields.Integer(compute="_compute_th_quantity_prm")
    th_quantity_pom = fields.Integer(compute="_compute_th_quantity_pom")
    activity_ids = fields.One2many('mail.activity', 'calendar_event_id', string='Activities')

    th_bank = fields.Char(string="Ngân hàng", tracking=True)
    th_account_name = fields.Char(string="Tên tài khoản", tracking=True)
    th_account_number = fields.Char(string="Số tài khoản", tracking=True)
    th_account_branch = fields.Char(string="Chi nhánh", tracking=True)
    th_tax_no = fields.Char(string="Mã số thuế",compute="_compute_partner_values",inverse='_inverse_th_tax_no', tracking=True)
    th_contract_number = fields.Char(string="Số hợp đồng", tracking=True)
    th_contract_sign_date = fields.Date(string="Ngày ký hợp đồng", tracking=True)
    th_contract_file = fields.Many2many(comodel_name="ir.attachment", string="Tệp đính kèm", tracking=True)
    th_commission_policy = fields.Many2one(comodel_name="prm.commission.policy", string="Chính sách hợp tác")
    th_ownership_unit_id = fields.Many2one("th.ownership.unit", string="Đơn vị sở hữu")

    def action_open_form(self):
        return {
            'name': 'Hồ sơ đối tác',
            'view_mode': 'form',
            'res_model': 'th.partner.profile',
            'type': 'ir.actions.act_window',
            'target': 'current',
            'res_id': self.id,
        }

    def action_open_lead_prm(self):
        self.ensure_one()
        return {
            'name': 'Cơ hội PRM',
            'view_mode': 'tree',
            'res_model': 'prm.lead',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': [('th_partner_id', '=', self.th_partner_id.id)],
            'context': {'create': False,
                        },
        }

    def action_open_lead_pom(self):
        self.ensure_one()
        return {
            'name': 'Cơ hội POM',
            'view_mode': 'tree',
            'res_model': 'pom.lead',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'domain': [('th_partner_id', '=', self.th_partner_id.id)],
            'context': {'create': False,
                        },
        }

    def _compute_th_quantity_prm(self):
        for rec in self:
            rec.th_quantity_prm = len(self.env['prm.lead'].search([('th_partner_id', '=', self.th_partner_id.id)]))

    def _compute_th_quantity_pom(self):
        for rec in self:
            rec.th_quantity_pom = len(self.env['pom.lead'].search([('th_partner_id', '=', self.th_partner_id.id)]))

    @api.depends('th_partner_id')
    def _compute_name_profile(self):
        for rec in self:
            rec.name = f'Hồ sơ {rec.th_partner_id.name}' if rec.th_partner_id else 'Mới'

    @api.depends('th_partner_id')
    def _compute_partner_values(self):
        for rec in self:
            if not rec.th_partner_id:
                return False
            rec.th_prm_phone = rec.th_partner_id.phone
            rec.th_prm_phone2 = rec.th_partner_id.th_phone2
            rec.th_prm_email = rec.th_partner_id.email
            rec.th_tax_no = rec.th_partner_id.vat
            rec.th_street = rec.th_partner_id.street
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

    def _inverse_th_prm_phone(self):
        for rec in self:
            if not rec.th_partner_id: return
            rec.th_partner_id.phone = rec.th_prm_phone

    def _inverse_th_prm_phone2(self):
        for rec in self:
            if not rec.th_partner_id: return
            rec.th_partner_id.th_phone2 = rec.th_prm_phone2

    def _inverse_th_prm_email(self):
        for rec in self:
            if not rec.th_partner_id: return
            rec.th_partner_id.email = rec.th_prm_email

    def _inverse_th_tax_no(self):
        for rec in self:
            if not rec.th_partner_id: return
            rec.th_partner_id.vat = rec.th_tax_no