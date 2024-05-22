from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _, exceptions
from odoo.exceptions import ValidationError
import xmlrpc.client
from odoo.exceptions import UserError
import json


class PRMLead(models.Model):
    _name = "prm.lead"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Quản lý quan hệ đối tác"
    _order = 'th_last_check desc, th_partner_code asc'

    name = fields.Char(string='Tên cơ hội', store=True, default="MỚI")
    name_id_sequence = fields.Char()
    th_user_id = fields.Many2one('res.users', string='Người phụ trách', tracking=True,
                                 default=lambda self: self.env.user.id)
    th_partner_id = fields.Many2one(comodel_name="res.partner", domain="[('id', 'in', [])]", string="Tên đối tác",
                                    index=True, tracking=True)
    active = fields.Boolean('Active', default=True, tracking=True)
    th_partner_code = fields.Char(related="th_partner_id.th_customer_code", string="Mã đối tác")
    th_partner_phone = fields.Char(string="Điện thoại", related="th_partner_id.phone", tracking=True)
    th_partner_phone2 = fields.Char(string="Điện thoại 2", related="th_partner_id.th_phone2", tracking=True)
    th_partner_email = fields.Char(string="Email", related="th_partner_id.email", tracking=True)
    th_check_phone = fields.Char(string="Điện thoại")
    th_check_email = fields.Char(string="Email")
    th_module_ids = fields.Many2many(comodel_name="therp.module", string="Module",
                                     default=lambda self: self.env.ref('th_setup_parameters.th_prm_module').ids)
    th_type = fields.Selection(string="Loại", selection=[('prm', 'PRM')], default='prm', store=True)
    th_stage_id = fields.Many2one(comodel_name="prm.level", string="Mối quan hệ", domain="[('th_type', '=', 'prm')]",
                                  required=True, tracking=True, default=lambda self: self.env['prm.level'].search(
            [('th_type', '=', 'prm'), ('th_first_status', '=', True)]).id)
    th_first_status_stage = fields.Boolean(related="th_stage_id.th_first_status", string="Trạng thái đầu")
    th_last_status_stage = fields.Boolean(related="th_stage_id.th_last_status")
    th_partner_level = fields.Selection(selection=[('agent_level_1', 'Đại lý cấp 1'),
                                                   ('agent_level_2', 'Đại lý cấp 2'),
                                                   ('agent_level_3', 'Đại lý cấp 3'),
                                                   ('agent_level_4', 'Đại lý cấp 4')], string="Cấp đại lý",
                                        tracking=True)
    th_partner_category = fields.Selection(string="Loại đối tác",
                                           selection=[('affiliate', 'Affiliate'), ('agent', 'Đại lý')], tracking=True)
    th_last_check = fields.Datetime(string="Liên hệ lần cuối", default=lambda self: fields.Datetime.now(),
                                    tracking=True)
    th_description = fields.Text(string="Mô tả", tracking=True)
    th_partner_reference_id = fields.Many2one(comodel_name="res.partner", string="Người giới thiệu")
    th_affiliate_marketing_code = fields.Char(related="th_partner_reference_id.th_affiliate_code",
                                              string="Mã tiếp thị liên kết", store=True)
    th_commission_policy = fields.Many2one(comodel_name="prm.commission.policy", string="Chính sách hợp tác",
                                           tracking=True)
    th_partner_group_ids = fields.Many2many(comodel_name="prm.partner.group", relation="prm_partner_group_prm_lead_rel",
                                            string="Nhóm đối tác")
    th_par_gr_display = fields.Char(string='Xuất - Nhóm đối tác', compute='_compute_par_gr_display')
    th_partner_source_id = fields.Many2one(comodel_name="prm.partner.source", string="Nguồn đối tác", tracking=True)
    th_collaborative_products_ids = fields.Many2many(comodel_name="prm.collaborative.products",
                                                     relation="collaborative_products_prm_lead_rel",
                                                     string="Sản phẩm hợp tác")
    th_col_pro_display = fields.Char(string='Xuất - Sản phẩm hợp tác', compute='_compute_col_pro_display')
    th_call_status_detail_id = fields.Many2one(comodel_name="th.status.detail", string="Trạng thái chi tiết",
                                               domain="[('th_prm_level', '=?', th_stage_id), ('th_status_category_id', '=?', th_call_status)]",
                                               default=lambda self: self.env['th.status.detail'].search(
                                                   [('th_type', '=', 'prm')], limit=1), tracking=True)
    th_call_status = fields.Many2one(comodel_name="th.status.category", string="Tình trạng gọi",
                                     domain="[('th_prm_level_category', '=?', th_stage_id)]",
                                     default=lambda self: self.env['th.status.category'].search(
                                         [('th_type', '=', 'prm')], limit=1), tracking=True)
    th_date_to_level_up_p4 = fields.Date(string="Ngày lên level P4")
    th_date_to_level_up_p5 = fields.Date(string="Ngày lên level P5")
    th_date_to_level_up_p6 = fields.Date(string="Ngày lên level P6")
    th_contract_number = fields.Char(string="Số hợp đồng", tracking=True)
    th_contract_sign_date = fields.Date(string="Ngày ký hợp đồng", tracking=True)
    th_contract_file = fields.Many2many(comodel_name="ir.attachment", string="Tệp đính kèm", tracking=True)
    th_reuse_source = fields.Char(string="Tên nguồn TSD")
    th_reuse = fields.Char(string="Tái sử dụng")
    th_storage = fields.Boolean(string="Lưu trữ", default=False)
    th_pom_lead_count = fields.Integer(compute="_compute_th_pom_lead_count")
    th_team_id = fields.Many2one(comodel_name="prm.team", string="Đội/nhóm")
    th_team_leader_ids = fields.Many2many(comodel_name="res.users", relation="th_team_leader_prm_rel", string="Quản lý",
                                          store=True, compute="_compute_th_team_leader_ids")
    th_ownership_unit_id = fields.Many2one("th.ownership.unit", string="Đơn vị sở hữu", readonly=False)
    th_data_getfly = fields.Text("Data Getfly")
    th_lead_aff_id = fields.Char(string='Cơ hội bên aff')
    th_work_unit = fields.Char(string="Đơn vị công tác")
    th_check_partner_referred = fields.Boolean(copy=False)
    th_bank_ids = fields.One2many(related="th_partner_id.bank_ids")
    th_check_aff = fields.Boolean(string="Check tài khoản aff")
    th_city_id = fields.Many2one("res.country.state", string="Tỉnh/Thành phố",
                                 domain="[('country_id.code', '=', 'VN')]")
    th_district_id = fields.Many2one("th.country.district", string="Quận/Huyện",
                                     domain="[('th_state_id', '=', th_city_id)]")
    th_ward_id = fields.Many2one("th.country.ward", string="Phường/Xã",
                                 domain="[('th_district_id', '=', th_district_id)]")
    th_duplicate_lead_formio = fields.Boolean(string="Check trùng cơ hội từ form nhúng", default=False)
    th_date_duplicate_lead = fields.Date(string="Ngày tạo cơ hội trùng")

    @api.onchange('th_check_phone')
    def onchange_th_check_phone(self):
        self.ensure_one()
        if self.th_check_phone:
            partner = self.env['res.partner'].search(
                ['|', ('phone', '=', self.th_check_phone), ('th_phone2', '=', self.th_check_phone)], limit=1)
            if partner:
                duplicate_lead = self.env['prm.lead'].sudo().search(
                    [('th_partner_id', '=', partner.id), ('th_partner_id', '!=', False),
                     ('th_ownership_unit_id', '=', self.th_ownership_unit_id.id)], limit=1)
                if duplicate_lead:
                    error_message = _(
                        "Trùng cơ hội với tên đối tác '%s', Số điện thoại '%s', Số điện thoại 2 '%s', Email '%s', Người phụ trách '%s'!") % (
                                        duplicate_lead.th_partner_id.name, duplicate_lead.th_partner_phone or '',
                                        duplicate_lead.th_partner_phone2 or '',
                                        duplicate_lead.th_partner_email or '', duplicate_lead.th_user_id.name or '')
                    raise UserError(error_message)
                else:
                    self.th_partner_id = partner

    @api.onchange('th_check_email')
    def onchange_th_check_email(self):
        self.ensure_one()
        if self.th_check_email:
            partner = self.env['res.partner'].search([('email', '=', self.th_check_email)], limit=1)
            if partner:
                duplicate_lead = self.env['prm.lead'].sudo().search(
                    [('th_partner_id', '=', partner.id), ('th_partner_id', '!=', False),
                     ('th_ownership_unit_id', '=', self.th_ownership_unit_id.id)], limit=1)
                if duplicate_lead:
                    error_message = _(
                        "Trùng cơ hội với tên đối tác '%s', số điện thoại '%s', email '%s', người phụ trách '%s'!") % (
                                        duplicate_lead.th_partner_id.name, duplicate_lead.th_partner_phone or '',
                                        duplicate_lead.th_partner_email, duplicate_lead.th_user_id.name or '')
                    raise UserError(error_message)
                else:
                    self.th_partner_id = partner

    @api.onchange('th_call_status')
    def onchange_th_call_status(self):
        if self.th_call_status_detail_id and self.th_call_status_detail_id.id not in self.th_call_status.th_status_detail_ids.ids:
            self.th_call_status_detail_id = False

    @api.depends('th_user_id')
    def _compute_th_ownership_unit_id(self):
        for rec in self:
            if rec.th_user_id:
                team = self.env['prm.team'].search(
                    ['|', ('manager_id', '=', rec.th_user_id.ids), ('th_member_ids', 'in', rec.th_user_id.ids)],
                    limit=1, order='id ASC')
                if team:
                    self.th_ownership_unit_id = team.th_ownership_unit_team_id.id
                else:
                    self.th_ownership_unit_id = False

    @api.constrains('th_partner_id')
    def _check_duplicate_values(self):
        for rec in self:
            check_opportunity = self.sudo().search([
                ('id', '!=', rec.id),
                ('th_partner_id', '=', rec.th_partner_id.id),
                ('th_partner_id', '!=', False),
                ('th_ownership_unit_id', '=', rec.th_ownership_unit_id.id)
            ], limit=1)
            if check_opportunity:
                val_name = check_opportunity.th_partner_id.name
                val_user = check_opportunity.th_user_id.name or ''
                val_phone = check_opportunity.th_partner_phone or ''
                val_email = check_opportunity.th_partner_email or ''
                raise ValidationError(
                    _("Trùng cơ hội với tên đối tác '%s' , số điện thoại '%s' , email '%s' , người phụ trách '%s' !") % (
                        val_name, val_phone, val_email, val_user))

    @api.depends('th_user_id', 'th_user_id.th_team_leader_ids')
    def _compute_th_team_leader_ids(self):
        for rec in self:
            rec.th_team_leader_ids = False
            if rec.th_user_id:
                parent_team = self.env['prm.team'].search(
                    ['|', ('manager_id', '=', rec.th_user_id.id), ('th_member_ids', 'in', rec.th_user_id.ids)])

                rec.th_team_leader_ids = [(6, 0, parent_team.mapped('manager_id').ids)]

    def action_open_profile(self):
        self.ensure_one()
        return {
            'name': 'Hồ sơ',
            'view_mode': 'form',
            'res_model': 'res.partner',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self.th_partner_id.id,
            'domain': [('id', '=', self.th_partner_id.id)],
        }

    @api.depends('th_stage_id')
    def _compute_type(self):
        for rec in self:
            rec.th_type = rec.th_stage_id.th_type

    @api.depends('th_last_status_stage')
    def _compute_th_pom_lead_count(self):
        for rec in self:
            rec.th_pom_lead_count = 0
            if rec.th_last_status_stage:
                pom_lead = self.env['pom.lead'].sudo().search([('th_prm_lead_id', '=', rec.id)], limit=1)
                rec.th_pom_lead_count = len(pom_lead)

    def _inverse_th_address(self):
        for rec in self:
            if not rec.th_partner_id: return
            rec.th_partner_id.street = rec.th_address

    def action_change_state_to_pom(self):
        values = {
            'th_partner_id': self.th_partner_id.id,
            'th_user_id': self.th_user_id.id,
            'th_partner_level': self.th_partner_level,
            'th_partner_group_ids': self.th_partner_group_ids.ids,
            'th_collaborative_products_ids': self.th_collaborative_products_ids.ids,
            'th_partner_source_id': self.th_partner_source_id.id,
            'th_commission_policy': self.th_commission_policy.id,
            'th_contract_number': self.th_contract_number,
            'th_contract_sign_date': self.th_contract_sign_date,
            'th_contract_file': self.th_contract_file,
            'th_partner_reference_id': self.th_partner_reference_id.id,
            'th_affiliate_marketing_code': self.th_affiliate_marketing_code,
            'th_ownership_unit_id': self.th_ownership_unit_id.id,
            'th_prm_lead_id': self.id,
            'th_level_up_date_c0': self.th_date_to_level_up_p6,
        }
        self.env["pom.lead"].sudo().create(values)
        for record in self:
            if not record.th_partner_phone or not record.th_partner_email:
                raise UserError(
                    "Vui lòng điền vào các trường 'Điện thoại' và 'Email' trước khi chuyển sang trạng thái POM !")

        return True

    def open_budget_form_view(self):
        return {
            'type': 'ir.actions.act_window',
            'res_model': 'prm.lead',
            'res_id': self.id,
            'view_mode': 'form',
            'views': [(False, "form")],
            'target': 'current',
            'context': {'default_th_type': 'prm'},
        }

    def check_last_status(self):
        if any(self.filtered(
                lambda d: d.th_stage_id and d.th_stage_id.th_last_status == True and d.th_pom_lead_count != False)):
            return True

    def th_action_archive(self):
        for rec in self:
            rec.th_storage = True
            # rec.th_old_user_id = rec.th_user_id
            rec.th_user_id = False
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_create_reuse(self):
        context = self.env.context.copy()
        context.update({'default_th_create_reuse': True})
        self.env['prm.lead.reuse'].browse(self._context.get('active_id')).th_create_reuse = True
        return {
            'name': 'Cấu hình',
            'view_mode': 'form',
            'res_model': 'prm.lead.reuse',
            'type': 'ir.actions.act_window',
            'target': 'new',
            'res_id': self._context.get('active_id'),
            'context': context,
        }

    def action_open_pom_lead(self):
        pom_lead = self.env['pom.lead'].sudo().search([('th_prm_lead_id', '=', self.id)], limit=1)
        if not pom_lead:
            return
        return {
            'name': 'POM',
            'view_mode': 'form',
            'res_model': 'pom.lead',
            'type': 'ir.actions.act_window',
            'res_id': pom_lead.id,
            'context': {'create': False, 'edit': False, 'delete': False, 'copy': False, 'not_open_prm': True},
        }

    def update_th_last_check(self):
        self.update({'th_last_check': fields.Datetime.now()})

    @api.depends('th_partner_group_ids')
    def _compute_col_pro_display(self):
        for record in self:
            record.th_col_pro_display = ', '.join(record.th_collaborative_products_ids.mapped('display_name'))

    @api.depends('th_partner_group_ids')
    def _compute_par_gr_display(self):
        for record in self:
            record.th_par_gr_display = ', '.join(record.th_partner_group_ids.mapped('display_name'))

    def write(self, vals):
        if 'th_call_status_detail_id' in vals and vals.get('th_call_status_detail_id'):
            for rec in self:
                vals['th_last_check'] = fields.Datetime.today()
        th_stage_id = vals.get('th_stage_id')
        if th_stage_id:
            stage = self.env['prm.level'].browse(th_stage_id)
            stage_name = stage.name if stage else ''
            if stage_name == 'P4' and not self.th_date_to_level_up_p4:
                vals['th_date_to_level_up_p4'] = fields.Date.today()
            elif stage_name == 'P5' and not self.th_date_to_level_up_p5:
                vals['th_date_to_level_up_p5'] = fields.Date.today()
            elif stage_name == 'P6' and not self.th_date_to_level_up_p6:
                vals['th_date_to_level_up_p6'] = fields.Date.today()
        if vals.get('th_partner_reference_id', ''):
            for rec in self:
                rec.th_check_partner_referred = True
        return super(PRMLead, self).write(vals)

    @api.ondelete(at_uninstall=False)
    def _unlink_prm_record(self):
        for rec in self:
            if rec.th_pom_lead_count != False:
                raise exceptions.UserError(_('Không thể xóa bản ghi đã tồn tại POM'))

    @api.model
    def _check_import_records(self, vals_list):
        for vals in vals_list:
            th_stage_id = vals.get('th_stage_id')
            if th_stage_id:
                stage = self.env['prm.level'].search([('id', '=', th_stage_id), ('th_type', '=', 'prm')])
                if not stage:
                    raise exceptions.ValidationError(_('Mối quan hệ không hợp lệ.'))

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('import_file'):
            self._check_import_records(vals_list)
        if self._context.get('aff_prm_lead'):
            vals_list1 = []
            for vals in vals_list:
                vals_list1.append(self.create_lead_aff(vals))
            vals_list = vals_list1
        for vals in vals_list:
            if vals.get('th_partner_reference_id', ''):
                vals['th_check_partner_referred'] = True
        res = super().create(vals_list)
        self.clear_caches()
        if res.th_affiliate_marketing_code and not self._context.get('aff_prm_lead', False) and not self._context.get(
                'th_test_import', False):
            self.action_synchronize_data_api([], res)
        name_id = self.env['ir.sequence'].next_by_code('prm.code')
        if res.name == 'MỚI':
            res.name_id_sequence = name_id
            res.name = "[" + name_id + "]" + "_" + str(res.th_partner_code) + "_" + res.th_partner_id.display_name
        return res

    @api.model
    def create_lead_aff(self, vals):
        th_ownership = self.env['th.ownership.unit'].search([('th_code', '=', vals.get('th_ownership_unit_code'))],
                                                            limit=1)
        th_partner_reference_id = self.env['res.partner'].search(
            [('th_affiliate_code', '=', vals.get('th_affiliate_code', 'ko co reference'))], limit=1)
        partner_aff = self.env['res.partner'].search(
            ['|', ('email', '=', vals.get('th_email', 'Không có Email')),
             ('phone', '=', vals.get('th_phone', 'Không có số điện thoại'))], limit=1)
        if not partner_aff:
            partner_aff = self.env['res.partner'].create({
                'name': vals.get('name_customer', False),
                'phone': vals.get('th_phone', False),
                'email': vals.get('th_email', False),
                'th_module_ids': [(4, self.env.ref('th_setup_parameters.th_prm_module').id)],

            })
        new_opportunity = {
            'th_partner_id': partner_aff.id,
            'th_ownership_unit_id': th_ownership.id,
            'th_partner_reference_id': th_partner_reference_id.id if th_partner_reference_id else False,
            'th_lead_aff_id': vals.get('id', False),
        }
        return new_opportunity

    def action_api_create_user(self):
        if not self.th_partner_email:
            raise ValidationError('Vui lòng điền email để tạo tài khoản affiliate!')

        server_api = self.env['th.api.server'].search([('state', '=', 'deploy'), ('th_type', '=', 'aff')], limit=1,
                                                      order='id desc')
        if not server_api:
            return False

        try:
            result_apis = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(server_api.th_url_api))
            result_apis.execute_kw(server_api.th_db_api, server_api.th_uid_api, server_api.th_password, 'res.partner',
                                   'check_access_rights', ['read'], {'raise_exception': False})
            user_exists = result_apis.execute_kw(server_api.th_db_api, server_api.th_uid_api, server_api.th_password,
                                                 'res.users', 'search_read', [[['login', '=', self.th_partner_email],
                                                                               ['active', 'in', [False, True]]]],
                                                 {'fields': ['active'], 'limit': 1})
            for rec in user_exists:
                if rec['active']:
                    raise ValidationError(_('Tài khoản đã được tạo!'))
                else:
                    return result_apis.execute_kw(server_api.th_db_api, server_api.th_uid_api, server_api.th_password,
                                                  'res.users', 'write', [[rec['id']], {'active': True}])
            val = {
                'name': self.th_partner_id.name,
                'email': self.th_partner_email,
                'phone': self.th_partner_phone,
                'th_affiliate_code': self.th_partner_id.th_affiliate_code,
                'th_customer_code': self.th_partner_id.th_customer_code,
                'th_own_code_samp': self.th_ownership_unit_id.th_code,
                'th_partner_samp': self.th_partner_id.id,
                # 'th_bank': self.th_partner_profile_id.th_bank,
                # 'th_account_name': self.th_partner_profile_id.th_account_name,
                # 'th_account_branch': self.th_partner_profile_id.th_account_branch,
                # 'th_account_number': self.th_partner_profile_id.th_account_number,
                'th_citizen_identification': self.th_partner_id.th_citizen_identification,
                'th_date_identification': self.th_partner_id.th_date_identification,
                'th_place_identification': self.th_partner_id.th_place_identification,
                'th_country': self.th_partner_id.country_id.name if self.th_partner_id.country_id else False,
                'th_district': self.th_partner_id.th_district_id.name if self.th_partner_id.th_district_id.name else False,
                'th_ward': self.th_partner_id.th_ward_id.name if self.th_partner_id.th_ward_id else False,
                'vat': self.th_partner_id.vat,
            }

            result_apis.execute_kw(server_api.th_db_api, server_api.th_uid_api, server_api.th_password, 'res.users',
                                   'create', [val], {'context': {'create_ctv': 'True'}})
            self.th_partner_id.sudo().write({'th_api_state': True})
            self.th_check_aff = True
        except Exception as e:
            self.th_partner_id.sudo().write({'th_api_state': False})
            print('Error API Pull', e)

    @api.model
    def receive_data_from_module(self, data_to_send):
        customer = self.env['res.partner'].search(
            [('phone', '=', data_to_send.get('phone_customer')), ('email', '=', data_to_send.get('mail_customer'))],
            limit=1)
        ctv = self.env['res.partner'].search([('th_affiliate_code', '=', data_to_send.get('th_affiliate_code'))])
        ownership_unit = self.env['th.ownership.unit'].search(
            [('th_code', '=', data_to_send.get('th_ownership_unit_id'))], limit=1)
        if customer:
            if not self.search([('th_partner_id', '=', customer.id)]):
                self.env['prm.lead'].create([{'th_partner_id': customer.id,
                                              'th_description': data_to_send.get('th_description'),
                                              'th_partner_reference_id': ctv.id if ctv else False,
                                              'th_lead_aff_id': data_to_send.get('id_customer'),
                                              'th_ownership_unit_id': ownership_unit.id if ownership_unit else self.env[
                                                  'th.ownership.unit'].search([('th_code', '=', 'aum')], limit=1).id,
                                              }])

        elif not customer:
            partner_id = self.env['res.partner'].create([{'name': data_to_send.get('name_customer'),
                                                          'phone': data_to_send.get('phone_customer'),
                                                          'email': data_to_send.get('mail_customer')}])

            self.env['prm.lead'].create([{'th_partner_id': partner_id.id,
                                          'th_description': data_to_send.get('th_description'),
                                          'th_partner_reference_id': ctv.id if ctv else False,
                                          'th_ownership_unit_id': ownership_unit.id if ownership_unit else self.env[
                                              'th.ownership.unit'].search([('th_code', '=', 'aum')], limit=1).id,
                                          'th_lead_aff_id': data_to_send.get('id_customer'),
                                          }])

    def get_vals_opportunity_aff(self, res):
        data = {}
        for rec in res:
            data['th_lead_id_samp'] = rec.id
            if rec.name:
                data['name'] = rec.name
            if rec.th_partner_reference_id:
                data['th_affiliate_code'] = rec.th_affiliate_marketing_code
            if rec.th_partner_id:
                data['th_customer'] = rec.th_partner_id.name
                data['th_customer_code'] = rec.th_partner_id.th_customer_code
            if rec.th_description:
                data['th_description'] = rec.th_description
            if rec.th_call_status:
                data['th_status_category'] = rec.th_call_status.name
            if rec.th_call_status_detail_id:
                data['th_status_detail'] = rec.th_call_status_detail_id.name
            if rec.th_stage_id:
                data['th_stage'] = rec.th_stage_id.name
            if rec.th_user_id:
                data['th_caregiver'] = rec.th_user_id.name
        return data

    def action_synchronize_data_api(self, data_code_aff=[], res=None):
        server_api = self.env['th.api.server'].search([('state', '=', 'deploy'), ('th_type', '=', 'aff')], limit=1,
                                                      order='id desc')
        if not server_api:
            return False
        try:
            record = self.search([('th_affiliate_marketing_code', 'in', data_code_aff)])
            if res:
                record = res
            if self._context.get('th_schedule', False):
                today = fields.Datetime.now()
                record = record.filtered(
                    lambda d: today.replace(hour=0, minute=0, second=0, microsecond=0) - relativedelta(
                        days=1) <= d.write_date <= today)
            result_apis = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(server_api.th_url_api))
            db = server_api.th_db_api
            uid_api = server_api.th_uid_api
            password = server_api.th_password

            for rec in record:
                values = self.get_vals_opportunity_aff(rec)
                context = {'module': self.env.ref('th_setup_parameters.th_prm_module').name,
                           'company_code': rec.th_ownership_unit_id.th_code,
                           'th_create': True if not rec.th_lead_aff_id else False,
                           'th_opportunity_aff_id': [int(rec.th_lead_aff_id)] if rec.th_lead_aff_id else [],
                           }
                res_id = result_apis.execute_kw(db, uid_api, password, 'th.opportunity.ctv', 'receive_data',
                                                [[], values], {'context': context})
                rec.write({'th_lead_aff_id': int(res_id.get('id', False))})
        except Exception as e:
            print(e)
        return True

    def th_schedule_action_synchronize_data_api(self):
        server_api = self.env['th.api.server'].search([('state', '=', 'deploy'), ('th_type', '=', 'aff')], limit=1,
                                                      order='id desc')
        if not server_api:
            return False
        try:
            result_apis = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(server_api.th_url_api))
            db = server_api.th_db_api
            uid_api = server_api.th_uid_api
            password = server_api.th_password
            data_code_aff = result_apis.execute_kw(db, uid_api, password, 'th.opportunity.ctv',
                                                   'th_action_synchronize_data', [[], True])
            self.action_synchronize_data_api([data for data in data_code_aff if data != False], res=None)
        except Exception as e:
            print(e)
        return True

    def get_current_record_url(self):
        url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        url += '/web?db=%s#id=%s&view_type=form&model=prm.lead' % (self.env.cr.dbname, self.id)
        return url
