import xmlrpc

from odoo import fields, models, api, _, exceptions


class POMLead(models.Model):
    _name = "pom.lead"
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = "Quản lý điều hành đối tác"
    _order = 'th_last_check desc, th_partner_code asc'

    name = fields.Char(string='Tên cơ hội', compute='_compute_name', readonly=False, store=True)
    th_user_id = fields.Many2one('res.users', string='Người phụ trách', tracking=True)
    th_partner_id = fields.Many2one(comodel_name="res.partner", string="Tên đối tác", required=True, index=True,
                                    tracking=True)
    active = fields.Boolean('Active', default=True, tracking=True)
    th_partner_code = fields.Char(related="th_partner_id.th_customer_code", string="Mã đối tác")
    th_partner_phone = fields.Char(string="Điện thoại", related="th_partner_id.phone")
    th_partner_phone2 = fields.Char(string="Điện thoại 2", related="th_partner_id.th_phone2")
    th_partner_email = fields.Char(string="Email", related="th_partner_id.email")
    th_type = fields.Selection(string="Loại", selection=[('pom', 'POM')], default='pom', store=True)
    th_stage_id = fields.Many2one(comodel_name="prm.level", string="Mối quan hệ", domain="[('th_type', '=', 'pom')]",
                                  required=True, tracking=True, default=lambda self: self.env['prm.level'].search(
            [('th_type', '=', 'pom'), ('th_first_status', '=', True)]).id)
    th_partner_level = fields.Selection(selection=[('agent_level_1', 'Đại lý cấp 1'),
                                                   ('agent_level_2', 'Đại lý cấp 2'),
                                                   ('agent_level_3', 'Đại lý cấp 3'),
                                                   ('agent_level_4', 'Đại lý cấp 4')], string="Cấp đại lý",
                                        tracking=True)
    th_registration_date = fields.Date(string="Ngày đăng ký", tracking=True)
    th_partner_category = fields.Selection(string="Loại đối tác",
                                           selection=[('affiliate', 'Affiliate'), ('agent', 'Đại lý')], tracking=True)
    th_last_check = fields.Datetime(string="Liên hệ lần cuối", default=lambda self: fields.Datetime.now(),
                                    tracking=True)
    th_description = fields.Text(string="Mô tả", tracking=True)
    th_partner_reference_id = fields.Many2one(comodel_name="res.partner", string="Người giới thiệu")
    th_affiliate_marketing_code = fields.Char(related="th_partner_reference_id.th_affiliate_code",
                                              string="Mã tiếp thị liên kết")
    th_commission_policy = fields.Many2one(comodel_name="prm.commission.policy", string="Chính sách hợp tác",
                                           tracking=True)
    th_partner_status = fields.Selection(string="Trạng thái đối tác",
                                         selection=[('normal', 'Bình thường'), ('warning', 'Cảnh báo'),
                                                    ('alert', 'Báo động'), ('suspending', 'Tạm dừng'),
                                                    ('quit', 'Rời'), ('terminate', 'Chấm dứt')], default="normal")
    th_suspend_status = fields.Selection(string="Trạng thái tạm dừng",
                                         selection=[('take_care_later_3', 'Chăm sóc sau 3 tháng'),
                                                    ('take_care_later_6', 'Chăm sóc sau 6 tháng'),
                                                    ('confirm_resume', 'Xác nhận tiếp tục'),
                                                    ('continue_suspending', 'Tiếp tục tạm dừng'),
                                                    ('quit_partnership', 'Hủy bỏ quan hệ đối tác')])
    th_partner_group_ids = fields.Many2many(comodel_name="prm.partner.group", relation="prm_partner_group_pom_lead_rel",
                                            string="Nhóm đối tác")
    th_par_gr_display = fields.Char(string='Xuất - Nhóm đối tác', compute='_compute_par_gr_display')
    th_collaborative_products_ids = fields.Many2many(comodel_name="prm.collaborative.products",
                                                     relation="collaborative_products_pom_lead_rel",
                                                     string="Sản phẩm hợp tác")
    th_col_pro_display = fields.Char(string='Xuất - Sản phẩm hợp tác', compute='_compute_col_pro_display')
    th_partner_source_id = fields.Many2one(comodel_name="prm.partner.source", string="Nguồn đối tác", tracking=True)
    th_call_status_detail_id = fields.Many2one(comodel_name="th.status.detail", string="Trạng thái chi tiết",
                                               domain="[('th_prm_level', '=?', th_stage_id), ('th_status_category_id', '=?', th_call_status)]",
                                               default=lambda self: self.env['th.status.detail'].search(
                                                   [('th_type', '=', 'prm')], limit=1), tracking=True)
    th_call_status = fields.Many2one(comodel_name="th.status.category", string="Tình trạng gọi",
                                     domain="[('th_prm_level_category', '=?', th_stage_id)]",
                                     default=lambda self: self.env['th.status.category'].search(
                                         [('th_type', '=', 'prm')], limit=1), tracking=True)
    th_reason_quit_id = fields.Many2one(comodel_name="prm.reason.quit", string="Lý do ngừng hợp tác", tracking=True)
    th_reason_quit_detail_id = fields.Many2one(comodel_name="prm.reason.quit.detail", string="Chi tiết lý do ngừng",
                                               domain="[('th_reason_quit_id', '=', th_reason_quit_id)]", tracking=True)
    th_stop_date = fields.Date(string="Thời gian ngừng hợp tác", tracking=True)
    th_level_up_date = fields.Date(string="Ngày lên Level C1 - C4", tracking=True)
    th_level_up_date_c0 = fields.Date(string="Ngày lên Level C0", tracking=True)
    is_invisible_th_reason_quit_id = fields.Boolean(default=True)
    th_reuse_source = fields.Char(string="Tên nguồn TSD")
    th_storage = fields.Boolean(string="Lưu trữ", default=False)
    th_prm_lead_id = fields.Many2one(comodel_name="prm.lead", string="prm record")
    th_prm_lead_count = fields.Integer(compute="_compute_th_prm_lead_count")
    th_team_leader_ids = fields.Many2many(comodel_name="res.users", relation="th_team_leader_pom_rel", string="Quản lý",
                                          store=True, compute="_compute_th_team_leader_ids")
    th_ownership_unit_id = fields.Many2one("th.ownership.unit", string="Đơn vị sở hữu")
    th_api_state = fields.Boolean('Đã đẩy', default=True)
    th_contract_number = fields.Char(string="Số hợp đồng", tracking=True)
    th_contract_sign_date = fields.Date(string="Ngày ký hợp đồng", tracking=True)
    th_contract_file = fields.Many2many(comodel_name="ir.attachment", string="Tệp đính kèm", tracking=True)
    th_check_partner_referred = fields.Boolean()
    th_bank_ids = fields.One2many(related="th_partner_id.bank_ids")
    th_city_id = fields.Many2one("res.country.state", string="Tỉnh/Thành phố",
                                 domain="[('country_id.code', '=', 'VN')]")
    th_district_id = fields.Many2one("th.country.district", string="Quận/Huyện",
                                     domain="[('th_state_id', '=', th_city_id)]")
    th_ward_id = fields.Many2one("th.country.ward", string="Phường/Xã",
                                 domain="[('th_district_id', '=', th_district_id)]")

    @api.onchange('th_call_status')
    def onchange_th_call_status(self):
        if self.th_call_status_detail_id and self.th_call_status_detail_id.id not in self.th_call_status.th_status_detail_ids.ids:
            self.th_call_status_detail_id = False

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

    @api.onchange('th_reason_quit_id')
    def _onchange_th_reason_quit_id(self):
        if not self.th_reason_quit_id:
            self.th_reason_quit_detail_id = False

    @api.onchange('th_call_status_detail_id')
    def _onchange_th_call_status_detail_id(self):
        if not self.th_call_status_detail_id:
            self.th_reason_quit_id = False
            self.is_invisible_th_reason_quit_id = True
            return
        if (self.th_call_status_detail_id.name).lower() == 'ngừng hợp tác':
            self.is_invisible_th_reason_quit_id = False
        else:
            self.th_reason_quit_id = False
            self.is_invisible_th_reason_quit_id = True

    @api.onchange('th_call_status')
    def _onchange_th_call_status(self):
        if not self.th_call_status:
            self.th_call_status_detail_id = True

    @api.onchange('th_partner_status')
    def _onchange_th_partner_status(self):
        self.th_suspend_status = False

    def _compute_th_prm_lead_count(self):
        for rec in self:
            prm_lead = self.env['prm.lead'].sudo().search([('id', '=', rec.th_prm_lead_id.id)], limit=1)
            rec.th_prm_lead_count = len(prm_lead)

    def _compute_th_crm_lead_count(self):
        for rec in self:
            domain = ['&', '|', ('th_ownership_id.th_partner_id', '=', rec.th_partner_id.id),
                      ('th_partner_referred_id', '=', rec.th_partner_id.id), ('th_type', '=', 'crm')]
            crm_lead = self.env['crm.lead'].sudo().search(domain)
            rec.th_crm_lead_count = len(crm_lead)

    @api.depends('th_partner_id')
    def _compute_name(self):
        for rec in self:
            if rec.name or not rec.th_partner_id:
                return
            else:
                rec.name = "POM_%s" % rec.th_partner_id.display_name

    # @api.depends('th_partner_id')
    # def _compute_partner_values(self):
    #     for rec in self:
    #         if not rec.th_partner_id:
    #             return False
    #         rec.th_partner_phone = rec.th_partner_id.phone
    #         rec.th_partner_phone2 = rec.th_partner_id.th_phone2
    #         rec.th_partner_email = rec.th_partner_id.email

    # def _inverse_th_partner_phone(self):
    #     for rec in self:
    #         if not rec.th_partner_id: return
    #         rec.th_partner_id.phone = rec.th_partner_phone
    #
    # def _inverse_th_partner_phone2(self):
    #     for rec in self:
    #         if not rec.th_partner_id: return
    #         rec.th_partner_id.th_phone2 = rec.th_partner_phone2

    # def _inverse_th_partner_email(self):
    #     for rec in self:
    #         if not rec.th_partner_id: return
    #         rec.th_partner_id.email = rec.th_partner_email

    @api.depends('th_prm_lead_id')
    def _compute_prm_values(self):
        for rec in self:
            if not rec.th_prm_lead_id:
                return False
            rec.th_partner_level = rec.th_prm_lead_id.th_partner_level
            rec.th_partner_group_ids = rec.th_prm_lead_id.th_partner_group_ids
            rec.th_partner_source_id = rec.th_prm_lead_id.th_partner_source_id

    def _inverse_th_partner_level(self):
        for rec in self:
            if not rec.th_prm_lead_id: return
            rec.th_prm_lead_id.th_partner_level = rec.th_partner_level

    def _inverse_th_partner_group_ids(self):
        for rec in self:
            if not rec.th_prm_lead_id: return
            rec.th_prm_lead_id.th_partner_group_ids = rec.th_partner_group_ids

    def _inverse_th_partner_source_id(self):
        for rec in self:
            if not rec.th_prm_lead_id: return
            rec.th_prm_lead_id.th_partner_source_id = rec.th_partner_source_id

    def th_action_archive(self):
        for rec in self:
            rec.th_storage = True
            # rec.th_old_user_id = rec.th_user_id
            rec.th_user_id = False
            self.action_archive_user_api(rec)
        return {
            'type': 'ir.actions.client',
            'tag': 'reload',
        }

    def action_open_prm_lead(self):
        prm_lead = self.env['prm.lead'].sudo().search([('id', '=', self.th_prm_lead_id.id)], limit=1)
        if not prm_lead:
            return
        return {
            'name': 'PRM',
            'view_mode': 'form',
            'res_model': 'prm.lead',
            'type': 'ir.actions.act_window',
            'res_id': prm_lead.id,
            'context': {'create': False, 'edit': False, 'delete': False, 'copy': False, 'not_open_pom': True,
                        'th_partner_wizard_action_create_and_open': True},
        }

    def action_open_crm_lead(self):
        domain = ['&', '|', ('th_ownership_id.th_partner_id', '=', self.th_partner_id.id),
                  ('th_partner_referred_id', '=', self.th_partner_id.id), ('th_type', '=', 'crm')]
        return {
            'name': 'Cơ hội CRM',
            'type': 'ir.actions.act_window',
            'res_model': 'crm.lead',
            'view_mode': 'tree,from',
            'views': [(False, 'list'), (False, 'form')],
            'domain': domain,
            'context': {'create': False, 'edit': False, 'delete': False, 'copy': False},
        }

    def update_th_last_check(self):
        self.update({'th_last_check': fields.Datetime.now()})

    @api.model
    def _check_import_records(self, vals_list):
        for vals in vals_list:
            th_stage_id = vals.get('th_stage_id')
            if th_stage_id:
                stage = self.env['prm.level'].search([('id', '=', th_stage_id), ('th_type', '=', 'pom')])
                if not stage:
                    raise exceptions.ValidationError(_('Mối quan hệ không hợp lệ.'))

    @api.model_create_multi
    def create(self, vals_list):
        if self.env.context.get('import_file'):
            self._check_import_records(vals_list)
        res = super().create(vals_list)
        for vals in vals_list:
            if vals.get('th_partner_reference_id', ''):
                for rec in self:
                    rec.th_check_partner_referred = True
        self.clear_caches()
        return res

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
            vals['th_last_check'] = fields.Date.today()
        if 'th_stage_id' in vals and vals.get('th_stage_id'):
            vals['th_level_up_date'] = fields.Date.today()
        if 'th_reason_quit_id' in vals and vals.get('th_reason_quit_id'):
            vals['th_stop_date'] = fields.Date.today()
        if vals.get('th_partner_reference_id', ''):
            for rec in self:
                rec.th_check_partner_referred = True
        return super(POMLead, self).write(vals)

    def check_last_status(self):
        if any(self.filtered(lambda d: d.th_stage_id and d.th_stage_id.th_last_status and d.th_prm_lead_count != 0)):
            return True

    def open_records_in_tabs(self):
        # Lấy danh sách các bản ghi bạn muốn mở trong tab mới
        record_ids = self.ids

        # Tạo URL cho từng bản ghi
        base_url = '/web#id='
        urls = [base_url + str(record_id) for record_id in record_ids]

        # Chuyển danh sách URL thành một URL duy nhất
        combined_url = ','.join(urls)

        # Tạo hành động URL để mở các URL trong các tab mới
        action = {
            'type': 'ir.actions.act_url',
            'url': '/web?#action=' + '&view_type=form&model=' + self._name + '&id=' + str(self.id) + '&menu_id=' + str(
                self.env.ref('th_prm.pom_menu_lead').id) + '&action=',
            'target': 'new',
        }
        return action

    def unlink(self):
        for rec in self:
            self.action_archive_user_api(rec)
            if not rec.th_api_state:
                rec.write({'active': False})
                return False
        return super().unlink()

    def action_archive_user_api(self, pom):
        server_api = self.env['th.api.server'].search([('state', '=', 'deploy'), ('th_type', '=', 'aff')], limit=1,
                                                      order='id desc')
        if not server_api:
            return False

        try:
            result_apis = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(server_api.th_url_api))
            result_apis.execute_kw(server_api.th_db_api, server_api.th_uid_api, server_api.th_password,
                                   'res.partner', 'check_access_rights', ['read'], {'raise_exception': False})
            user_exists = result_apis.execute_kw(server_api.th_db_api, server_api.th_uid_api,
                                                 server_api.th_password, 'res.users', 'search_read',
                                                 [[['login', '=', pom.th_partner_email],
                                                   ['active', 'in', [False, True]]]],
                                                 {'fields': ['partner_id'], 'limit': 1})

            if user_exists:
                result_apis.execute_kw(server_api.th_db_api, server_api.th_uid_api, server_api.th_password, 'res.users',
                                       'write', [[user_exists[0]['id']], {'active': False}])
                result_apis.execute_kw(server_api.th_db_api, server_api.th_uid_api, server_api.th_password,
                                       'res.partner', 'write', [[user_exists[0]['partner_id'][0]], {'active': False}])
            pom.write({'th_api_state': True})
        except Exception as e:
            pom.write({'th_api_state': False})
            print(e)
