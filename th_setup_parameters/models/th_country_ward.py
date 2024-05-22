import xmlrpc

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError

state = [('yes', 'Đã đẩy'), ('no', 'Chưa đẩy'), ('not_pull', 'Đẩy lỗi')]


class ThCountryWard(models.Model):
    _name = 'th.country.ward'
    _description = 'Phường/Xã'

    name = fields.Char(string='Phường/ Xã', required=True)
    th_ref = fields.Char(string='Mã Phường/ Xã', required=True)
    th_district_id = fields.Many2one(comodel_name='th.country.district', string='Quận/ Huyện', required=True)

    _sql_constraints = [
        ('name_th_ref_uniq', 'unique(th_district_id, th_ref)', 'Mã của Phường/Xã không được trùng ở mỗi Quận/Huyện !')
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
    #
    # @api.model
    # def create(self, vals_list):
    #     th_api, result_apis = self.th_api_search()
    #     if not self._context.get('import_file'):
    #         try:
    #             val = vals_list
    #             val.pop('th_api_state')
    #             result_apis.execute_kw(th_api.th_db_api, th_api.th_uid_api, th_api.th_password, 'th.country.ward', 'create', [val])
    #         except Exception as e:
    #             vals_list['th_api_state'] = 'not_pull'
    #         if vals_list.get('th_api_state', False) != 'not_pull':
    #             vals_list['th_api_state'] = 'yes'
    #     return super().create(vals_list)
    #
    # def write(self, vals):
    #     th_api, result_apis = self.th_api_search()
    #     exist_district = result_apis.execute_kw(th_api.th_db_api, th_api.th_uid_api, th_api.th_password, 'th.country.ward', 'search', [[['th_ref', '=', self.th_ref]]])
    #     if exist_district:
    #         try:
    #             val = vals
    #             val.pop('th_api_state')
    #             result_apis.execute_kw(th_api.th_db_api, th_api.th_uid_api, th_api.th_password, 'th.country.ward', 'write', [exist_district, val])
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
    #     th_api, result_apis = self.th_api_search()
    #     exist_district = result_apis.execute_kw(th_api.th_db_api, th_api.th_uid_api, th_api.th_password, 'th.country.ward', 'search', [[['th_ref', '=', self.th_ref]]])
    #     if exist_district:
    #         try:
    #             result_apis.execute_kw(th_api.th_db_api, th_api.th_uid_api, th_api.th_password, 'th.country.ward', 'unlink', [exist_district])
    #         except Exception as e:
    #             raise ValidationError(_('Không thể truy cập server api vui lòng xóa bản ghi trong thời gian gần nhất'))
    #     return super().unlink()
