import xmlrpc

from odoo import models, fields, api, exceptions, _
from odoo.exceptions import ValidationError
from odoo.osv import expression

state = [('yes', 'Đã đẩy'), ('no', 'Chưa đẩy'), ('not_pull', 'Đẩy lỗi')]


class ThCountryDistrict(models.Model):
    _name = 'th.country.district'
    _description = 'Quận/Huyện'

    name = fields.Char(string='Quận/ Huyện', required=True)
    th_ref = fields.Char(string='Mã Quận/ Huyện', required=True)
    th_state_id = fields.Many2one(comodel_name='res.country.state', required=True, string='Tỉnh/ Thành phố', domain="[('country_id.code', '=', 'VN')]")

    _sql_constraints = [
        ('name_th_ref_uniq', 'unique(th_state_id, th_ref)', 'Mã của Quận/Huyện không được trùng ở mỗi Tỉnh/TP !')
    ]

    # chưa cần tới api
    # def th_api_search(self):
    #     th_api = self.env['th.api.server'].search([('state', '=', 'deploy')], limit=1, order='id desc')
    #     if not th_api:
    #         return False
    #     try:
    #         result_apis = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(th_api.th_url_api))
    #     except Exception as e:
    #         return False
    #     return th_api, result_apis

    # @api.model
    # def create(self, vals_list):
    #     th_api, result_apis = self.th_api_search()
    #     db = th_api.th_db_api
    #     uid_api = th_api.th_uid_api
    #     password = th_api.th_password
    #     if not self._context.get('import_file'):
    #         try:
    #             val = vals_list
    #             val.pop('th_api_state')
    #             result_apis.execute_kw(db, uid_api, password, 'th.country.district', 'create', [val])
    #         except Exception as e:
    #             vals_list['th_api_state'] = 'not_pull'
    #         if vals_list.get('th_api_state', False) != 'not_pull':
    #             vals_list['th_api_state'] = 'yes'
    #     return super().create(vals_list)
    #
    # def action_synchronized(self):
    #     th_api, result_apis = self.th_api_search()
    #     districts = self.search([('th_api_state', '!=', 'yes')])
    #     if not districts or not th_api or not result_apis:
    #         return False
    #     db = th_api.th_db_api
    #     uid_api = th_api.th_uid_api
    #     password = th_api.th_password
    #
    #     for district in districts:
    #         check_syncs = result_apis.execute_kw(db, uid_api, password, 'th.country.district', 'search', [[['th_ref', '=', district.th_ref]]])
    #         state_id = result_apis.execute_kw(db, uid_api, password, 'res.country.state', 'search', [[['name', '=', district.th_state_id.name]]])
    #         val = {
    #             'name': district.name,
    #             'th_ref': district.th_ref,
    #             'th_state_id': state_id[0]
    #         }
    #         try:
    #             if check_syncs:
    #                 result_apis.execute_kw(db, uid_api, password, 'th.country.district', 'write', [check_syncs, val])
    #             else:
    #                 result_apis.execute_kw(db, uid_api, password, 'th.country.district', 'create', [val])
    #         except Exception as e:
    #             raise ValidationError(e)
    #         district.write({
    #             'th_api_state': 'yes'
    #         })
    #
    # def write(self, vals):
    #     th_api, result_apis = self.th_api_search()
    #     db = th_api.th_db_api
    #     uid_api = th_api.th_uid_api
    #     password = th_api.th_password
    #     exist_district = result_apis.execute_kw(db, uid_api, password, 'th.country.district', 'search', [[['th_ref', '=', self.th_ref]]])
    #     state_id = False
    #     if vals.get('th_state_id', False):
    #         th_state_id = self.env['res.country.state'].sudo().search([('id', '=', vals.get('th_state_id', False))])
    #         th_state_id = th_state_id if th_state_id else False
    #         state_id = result_apis.execute_kw(db, uid_api, password, 'res.country.state', 'search', [[['name', '=', th_state_id.name]]])
    #
    #     if exist_district:
    #         try:
    #             val = vals
    #             val.pop('th_api_state')
    #             if val.get('th_state_id', False):
    #                 val['th_state_id'] = state_id
    #             result_apis.execute_kw(db, uid_api, password, 'th.country.district', 'write', [exist_district, val])
    #         except Exception as e:
    #             vals['th_api_state'] = 'not_pull'
    #     else:
    #         vals['th_api_state'] = 'no'
    #
    #     if not vals.get('th_api_state', False):
    #         vals['th_api_state'] = 'yes'
    #     return super().write(vals)
    #
    # def unlink(self):
    #     res = super().unlink()
    #     th_api, result_apis = self.th_api_search()
    #     db = th_api.th_db_api
    #     uid_api = th_api.th_uid_api
    #     password = th_api.th_password
    #     exist_district = result_apis.execute_kw(db, uid_api, password, 'th.country.district', 'search', [[['th_ref', '=', self.th_ref]]])
    #     if exist_district:
    #         try:
    #             result_apis.execute_kw(db, uid_api, password, 'th.country.district', 'unlink', [exist_district])
    #         except Exception as e:
    #             raise ValidationError(e)
    #     return res
