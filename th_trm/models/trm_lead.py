import json
from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class ThTrmLead(models.Model):
    _name = "th.trm.lead"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Cơ hội sản xuất"

    def _domain_th_categ_id(self):
        return [('id', 'in', self.env['product.category'].search([]).filtered(lambda d: self.env.ref('th_setup_parameters.th_trm_module').id in d.th_module_ids.ids).ids)]

    name = fields.Char(string="Tên cơ hội", compute='_compute_name', tracking=True, store=True, default="MỚI")
    name_id_sequence = fields.Char()
    th_user_id = fields.Many2one(comodel_name="res.users", string="Người phụ trách", tracking=True,
                                 default=lambda self: self.env.user)
    th_trm_phone = fields.Char(string="Điện thoại", related="th_partner_id.th_trm_phone", tracking=True, store=True)
    th_trm_phone2 = fields.Char(string="Điện thoại 2", related="th_partner_id.th_trm_phone2", tracking=True, store=True)
    th_trm_email = fields.Char(string="Email", related="th_partner_id.th_trm_email", tracking=True, store=True)
    th_last_check = fields.Datetime(string="Liên hệ lần cuối", default=lambda self: fields.Datetime.today(),
                                    tracking=True)
    th_description = fields.Text(string='Mô tả', tracking=True)
    th_customer_code = fields.Char(string='Mã giảng viên', related="th_partner_id.th_customer_code", readonly=True,
                                   tracking=True)
    th_affiliate_code = fields.Char(string='Mã tiếp thị liên kết', related="th_partner_reference_id.th_affiliate_code",
                                    tracking=True)
    th_partner_reference_id = fields.Many2one(comodel_name="res.partner", string="Người giới thiệu")
    th_level_up_date = fields.Date(string="Ngày lên Level", default=fields.Date.today, tracking=True)
    stage_id = fields.Many2one(comodel_name="th.trm.stage", string="Mối quan hệ", tracking=True,
                               compute="_compute_stage_id", readonly=False, store=True)
    th_last_status_stage = fields.Boolean(related="stage_id.th_last_status")

    th_status_detail_id = fields.Many2one(comodel_name="th.status.detail", string="Trạng thái chi tiết",
                                          domain="[('th_trm_level_ids', '=?', stage_id), ('th_status_category_id', '=?', th_call_status)]",
                                          default=lambda self: self.env['th.status.detail'].search(
                                              [('th_type', '=', 'trm')], limit=1), tracking=True)
    th_call_status = fields.Many2one(comodel_name="th.status.category", string="Tình trạng gọi",
                                     domain="[('th_trm_level_category', '=?', stage_id)]",
                                     default=lambda self: self.env['th.status.category'].search(
                                         [('th_type', '=', 'trm')], limit=1), tracking=True)
    th_lecturer_profile_id = fields.Many2one(comodel_name="th.student.profile", string="Hồ sơ",
                                             compute="_compute_th_lecturer_profile_id")
    th_partner_id = fields.Many2one(comodel_name="th.lecturer.profile", string="Tên giảng viên", index=True, tracking=True)
    activity_ids = fields.One2many('mail.activity', 'calendar_event_id', string='Activities')
    th_trm_team_id = fields.Many2one(comodel_name="th.trm.team", string="Đội học liệu")
    th_team_leader_ids = fields.Many2many(comodel_name="res.users", relation="th_team_leader_rel", string="Quản lý",
                                          store=True, compute="_compute_th_team_leader_ids")
    th_categ_id = fields.Many2one("product.category", string="Danh mục sản phẩm", domain=_domain_th_categ_id)
    th_product = fields.Many2one(comodel_name="product.product", string="Tên môn sản xuất/ Khóa học sản xuất *",
                                 tracking=True,)
    th_domain_product = fields.Char(compute="_compute_th_domain_product")
    th_data_getfly = fields.Text("Data Getfly")
    th_trm_source = fields.Many2many("th.trm.source", relation="trm_source_trm_lead_rel", string="Nguồn khách hàng",
                                     tracking=True)
    th_trm_channel = fields.Many2many(comodel_name="th.trm.channel", relation="trm_channel_trm_lead_rel",
                                      string="Kênh thông tin")
    th_check_partner_referred = fields.Boolean(copy=False)

    @api.depends('th_categ_id')
    def _compute_th_domain_product(self):
        for rec in self:
            domain = []
            if rec.th_categ_id:
                domain.append(('categ_id', 'in', rec.th_categ_id.ids))
            else:
                domain.append(('categ_id', 'in', rec.env['product.category'].search([]).filtered(lambda lam: self.env.ref('th_setup_parameters.th_trm_module').id in lam.th_module_ids.ids).ids))
            rec.th_domain_product = json.dumps(domain)
    @api.onchange('th_call_status')
    def onchange_th_call_status(self):
        if self.th_status_detail_id and self.th_status_detail_id.id not in self.th_call_status.th_status_detail_ids.ids:
            self.th_status_detail_id = False

    @api.depends('th_user_id', 'th_user_id.th_team_leader_ids')
    def _compute_th_team_leader_ids(self):
        for rec in self:
            rec.th_team_leader_ids = False
            if rec.th_user_id:
                parent_team = self.env['th.trm.team'].search(
                    ['|', ('manager_id', '=', rec.th_user_id.id), ('th_member_ids', 'in', rec.th_user_id.ids)])

                rec.th_team_leader_ids = [(6, 0, parent_team.mapped('manager_id').ids)]

    def action_open_profile(self):
        self.ensure_one()
        return {
            'name': 'Hồ sơ',
            'view_mode': 'form',
            'res_model': 'th.lecturer.profile',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'context': {'create': False,
                        'default_th_partner_id': self.th_partner_id.id,
                        'invisible_button': True,
                        },
            'res_id': self.th_partner_id.id,
        }

    def _compute_th_lecturer_profile_id(self):
        for rec in self:
            rec.th_lecturer_profile_id = self.env['th.lecturer.profile'].search(
                [('th_partner_id', '=', self.th_partner_id.id)],
                limit=1).id if self.env[
                'th.lecturer.profile'].search([('th_partner_id', '=', self.th_partner_id.id)], limit=1) else False

    @api.depends('name')
    def _compute_stage_id(self):
        for rec in self:
            if not rec.stage_id:
                rec.stage_id = self.env['th.trm.stage'].search([], order="sequence, id", limit=1).id

    @api.model_create_multi
    def create(self, vals_list):
        res = super().create(vals_list)
        name_id = self.env['ir.sequence'].next_by_code('trm.code')
        for vals in vals_list:
            if vals.get('th_partner_reference_id', ''):
                for rec in res:
                    rec.th_check_partner_referred = True
        if res.name == 'MỚI':
            res.name_id_sequence = name_id
            res.name = "[" + name_id + "]" + "_" + str(res.th_customer_code) + "_" + res.th_partner_id.display_name
        return res

    def write(self, values):
        if 'th_status_detail_id' in values and values.get('th_status_detail_id'):
            for rec in self:
                values['th_last_check'] = fields.Date.today()

        if 'stage_id' in values and values.get('stage_id'):
            for rec in self:
                values['th_level_up_date'] = fields.Date.today()
        if values.get('th_partner_reference_id', ''):
            for rec in self:
                rec.th_check_partner_referred = True
        res = super(ThTrmLead, self).write(values)
        return res

    @api.constrains('th_partner_id', 'th_product')
    def _check_duplicate_values(self):
        for rec in self:
            check_opportunity = self.search([
                ('id', '!=', rec.id),
                ('th_partner_id', '=', rec.th_partner_id.id),
                ('th_categ_id', '=', rec.th_categ_id.id),
                ('th_product', '=', rec.th_product.id),
                ('th_trm_phone', '=', rec.th_trm_phone),
                ('th_trm_email', '=', rec.th_trm_email),
            ], limit=1)

            if check_opportunity:
                val_name = check_opportunity.th_partner_id.name
                val_user = check_opportunity.th_user_id.name or ''
                val_phone = check_opportunity.th_trm_phone or ''
                val_email = check_opportunity.th_trm_email or ''
                val_category = check_opportunity.th_categ_id.name or ''
                val_product = check_opportunity.th_product.name or ''
                raise ValidationError(
                    _("Trùng cơ hội với Tên giảng viên '%s', Số điện thoại '%s', Email '%s', Danh mục sản phẩm '%s', Tên môn sản xuất/ Khóa học sản xuất '%s', Người phụ trách '%s' !") % (
                    val_name, val_phone, val_email, val_category,
                    val_product, val_user))
