from odoo import fields,models, api, _
from odoo.exceptions import ValidationError

class ResPartner(models.Model):
    _inherit = "res.partner"

    def _th_domain_place_of_birth(self):
        state_id = self.env['res.country.state'].search([]).filtered(lambda u: u.country_id == self.env.ref('base.vn'))
        return [('id', 'in', state_id.ids)]

    # th_university_id = fields.Many2one(comodel_name="th.university", string="Trường học")
    th_origin_id = fields.Many2one(comodel_name="th.origin", string="Trường học")
    th_ward_id = fields.Many2one(comodel_name='th.country.ward', string='Phường/ Xã', domain="[('th_district_id', '=?', th_district_id), ('th_district_id.th_state_id', '=?', state_id)]", tracking=True)
    th_district_id = fields.Many2one(comodel_name='th.country.district', string='Quận/ Huyện', domain="[('th_state_id', '=?', state_id)]", tracking=True)

    th_customer_code = fields.Char(string="Mã Khách Hàng", tracking=True, copy=False)
    th_affiliate_code = fields.Char(string="Mã Tiếp Thị Liên Kết", tracking=True, copy=False)

    th_gender = fields.Selection(string="Giới tính", selection=[('male', 'Nam'), ('female', 'Nữ'), ('other', 'Khác'), ], tracking=True)
    th_birthday = fields.Date(string="Ngày sinh", tracking=True)
    th_place_of_birth_id = fields.Many2one(comodel_name="res.country.state", string="Nơi sinh")

    th_ethnicity_id = fields.Many2one(comodel_name="th.ethnicity", string="Dân tộc", tracking=True)
    th_religion_id = fields.Many2one(comodel_name="th.religion", string="Tôn giáo", tracking=True)

    th_phone2 = fields.Char(string="Số điện thoại 2", tracking=True)
    th_citizen_identification = fields.Char(string="Số CMT/ CCCD", tracking=True)
    th_date_identification = fields.Date(string="Ngày cấp CMT/ CCCD", tracking=True)
    th_place_identification = fields.Char(string="Nơi cấp CMT/ CCCD", tracking=True)
    th_citizen_identification_image = fields.Many2many(comodel_name="ir.attachment", string="Tệp đính kèm", tracking=True)
    th_module_ids = fields.Many2many(comodel_name="therp.module", string="Module")

    th_street = fields.Char(string="Địa chỉ (Hộ khẩu)")
    th_ward_permanent_id = fields.Many2one(comodel_name='th.country.ward', string='Phường/ Xã (Hộ khẩu)',
                                 domain="[('th_district_id', '=?', th_district_permanent_id), ('th_district_id.th_state_id', '=?', th_state_id)]",
                                 tracking=True)
    th_district_permanent_id = fields.Many2one(comodel_name='th.country.district', string='Quận/ Huyện (Hộ khẩu)',
                                     domain="[('th_state_id', '=?', th_state_id)]", tracking=True)
    th_state_id = fields.Many2one("res.country.state", string='Tỉnh/ TP (Hộ khẩu)', ondelete='restrict',
                                  domain="[('country_id', '=?', th_country_id)]")
    th_country_id = fields.Many2one('res.country', string='Quốc gia (Hộ khẩu)', ondelete='restrict')

    @api.constrains('phone', 'email', 'th_phone2')
    def _check_duplicate_values(self):
        for rec in self:
            check_partner = self.env['ir.config_parameter'].sudo().get_param('th_check_partner')
            ex_phone = ex_email = self.env['res.partner']
            val_phone = val_email = False
            if rec.phone:
                val_phone = self.search([('id', '!=', rec.id), '|', ('phone', '=', rec.phone), ('th_phone2', '=', rec.phone)])
                domain = [
                    ('id', '!=', rec.id), '|',
                    ('phone', '=', rec.phone if rec.phone else ' '),
                    ('th_phone2', '=', rec.phone if rec.phone else ' '),
                ]
                ex_phone = self.search(domain)
            if rec.email:
                val_email = self.search([('id', '!=', rec.id), ('email', '=', rec.email)])
                domain = [
                    ('id', '!=', rec.id),
                    ('email', '=', rec.email if rec.email else ' '),
                ]
                ex_email = self.search(domain)
            if check_partner and ex_phone and not ex_email:
                raise ValidationError(_("Trùng số điện thoại '%s' với tên liên hệ '%s'") % (rec.phone, ', '.join(val_phone.mapped('name'))))
            elif check_partner and not ex_phone and ex_email:
                raise ValidationError(_("Trùng email '%s' với tên liên hệ là '%s'") % (rec.email,  ', '.join(val_email.mapped('name'))))
            elif check_partner and ex_phone and ex_email:
                raise ValidationError(_("Trùng email '%s' với liên hệ '%s' và trùng số điện thoại '%s' với liên hệ '%s'") % (rec.email,  ', '.join(val_email.mapped('name')), rec.phone, ', '.join(val_phone.mapped('name'))))
            ex_partner = self.env['res.partner'].search([('id', '!=', rec.id),'|', ('phone', '=', rec.th_phone2), ('th_phone2', '=', rec.th_phone2),])
            if check_partner and rec.th_phone2 and ex_partner:
                raise ValidationError("Số điện thoại 2 đã bị trùng với số điện thoại 1 hoặc liên hệ khác !")

    @api.onchange('th_ward_id')
    def onchange_th_ward_id(self):
        if self.th_ward_id:
            self.th_district_id = self.th_ward_id.th_district_id.id
            self.state_id = self.th_district_id.th_state_id.id
            self.country_id = self.state_id.country_id.id

    @api.onchange('th_district_id')
    def onchange_th_district_id(self):
        if self.th_district_id:
            self.state_id = self.th_district_id.th_state_id.id
            self.country_id = self.state_id.country_id.id
        if self.th_district_id != self.th_ward_id.th_district_id:
            self.th_ward_id = False

    @api.onchange('country_id')
    def onchange_th_country_id(self):
        if self.country_id != self.state_id.country_id:
            self.state_id = False

    @api.onchange('state_id')
    def onchange_th_state_id(self):
        if self.state_id:
            self.country_id = self.state_id.country_id.id
        if self.state_id != self.th_district_id.th_state_id:
            self.th_district_id = False

    @api.onchange('th_ward_permanent_id')
    def onchange_th_ward_permanent_id(self):
        if self.th_ward_permanent_id:
            self.th_district_permanent_id = self.th_ward_permanent_id.th_district_id.id
            self.th_state_id = self.th_district_permanent_id.th_state_id.id
            self.th_country_id = self.th_state_id.country_id.id

    @api.onchange('th_district_permanent_id')
    def onchange_th_district_permanent_id(self):
        if self.th_district_permanent_id:
            self.th_state_id = self.th_district_permanent_id.th_state_id.id
            self.th_country_id = self.th_state_id.country_id.id
        if self.th_district_permanent_id != self.th_ward_permanent_id.th_district_id:
            self.th_ward_permanent_id = False

    @api.onchange('th_country_id')
    def onchange_th_country_permanent_id(self):
        if self.th_country_id != self.th_state_id.country_id:
            self.th_state_id = False

    @api.onchange('th_state_id')
    def onchange_th_state_permanent_id(self):
        if self.th_state_id:
            self.th_country_id = self.th_state_id.country_id.id
        if self.th_state_id != self.th_district_permanent_id.th_state_id:
            self.th_district_permanent_id = False

    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            if not vals.get('th_customer_code', False) or not vals.get('th_affiliate_code', False):
                vals['th_customer_code'] = self.env['ir.sequence'].next_by_code('customer.code')
                vals['th_affiliate_code'] = self.env['ir.sequence'].next_by_code('affiliate.code')
        return super(ResPartner, self).create(vals_list)