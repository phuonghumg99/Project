import xmlrpc

from odoo import fields, models, api, _
import json
from odoo.exceptions import ValidationError

class ThOrigin(models.Model):
    _name = "th.origin"
    _description = "Xuất xứ"

    name = fields.Char(string="Xuất xứ", required=True)
    th_code = fields.Char(string="Mã xuất xứ", required=True)
    th_university_major_ids = fields.One2many(comodel_name="th.university.major", inverse_name="th_origin_id", string="Ngành học")
    th_description = fields.Text(string="Mô tả")
    th_address = fields.Text(string="Địa chỉ")
    color = fields.Integer("Color Index", default=0)
    th_partner_id = fields.One2many(comodel_name="res.partner", inverse_name="th_origin_id", string="Liên hệ")
    th_api_state = fields.Boolean(default=True)
    active = fields.Boolean(default=True)
    th_module_ids = fields.Many2many(comodel_name="therp.module", string="Module")
    aff_warehouse_id = fields.Integer(string="Aff warehouse id", copy=False)

    @api.model
    def create(self, values):
        res = super(ThOrigin, self).create(values)
        self.update_th_warehouse(res, state='create')
        return res

    def write(self, values):
        res = super(ThOrigin, self).write(values)
        if values.get('aff_warehouse_id', '') == '' and any(values.get(f'{field}', False) for field in ['name', 'th_code', 'th_description', 'th_module_ids',]):
            self.update_th_warehouse(self, state='write')
        return res

    # def unlink(self):
    #     for rec in self:
    #         # self.update_th_warehouse(rec, state='unlink')
    #         if not rec.th_api_state:
    #             rec.write({'active': False})
    #             return False
    #     return super().unlink()

    def update_th_warehouse(self, res=None, state=None):
        server_api = self.env['th.api.server'].search([('state', '=', 'deploy'), ('th_type', '=', 'aff')], limit=1, order='id desc')
        if not server_api:
            return False
        try:
            result_apis = xmlrpc.client.ServerProxy('{}/xmlrpc/2/object'.format(server_api.th_url_api))
        except Exception as e:
            print(e)
            return False

        db = server_api.th_db_api
        uid_api = server_api.th_uid_api
        password = server_api.th_password

        if not res:
            res = self.search([])

        for rec in res:
            val = {
                'name': rec.name,
                'th_code': rec.th_code,
                'th_description': rec.th_description,
            }
            try:
                if state in ['create', 'write'] and not rec.aff_warehouse_id:
                    warehouse_id = result_apis.execute_kw(db, uid_api, password, 'th.warehouse', 'create', [val],
                                                          {'context': {'module': rec.th_module_ids.mapped('name')}})
                    rec.write({'aff_warehouse_id': warehouse_id})
                if state == 'write' and rec.aff_warehouse_id:
                    result_apis.execute_kw(db, uid_api, password, 'th.warehouse', 'write',
                                           [int(rec.aff_warehouse_id), val],
                                           {'context': {'module': rec.th_module_ids.mapped('name')}})
            except Exception as e:
                print(e)
        return True

    @api.constrains('th_code')
    def _constraint_th_code_origin(self):
        if any(self.search([('id', '!=', rec.id), ('th_code', '=', rec.th_code)]) for rec in self):
            raise ValidationError(_("Mã xuất xứ đã tồn tại. Vui lòng kiểm tra lại!"))


class ThMajor(models.Model):
    _name = "th.major"
    _description = "Ngành học"

    name = fields.Char(string="Tên ngành", required=True)
    # th_university_id = fields.Many2one(comodel_name="th.university", string="Trường đại học")
    th_description = fields.Text(string="Mô tả")
    th_major_code_aum = fields.Char(string="Mã ngành AUM", )


class ThUniversityMajor(models.Model):
    _name = "th.university.major"
    _description = "Trường - ngành"
    _rec_name = "th_major_id"

    th_major_id = fields.Many2one(comodel_name="th.major", string="Ngành học")
    th_major_code_university = fields.Char(string="Mã ngành", )
    # th_university_id = fields.Many2one(comodel_name="th.university", string="Trường đại học")
    th_origin_id = fields.Many2one(comodel_name="th.origin", string="Trường đại học")

    @api.constrains('th_major_id', 'th_origin_id')
    def _constraint_th_code_origin(self):
        if any(self.search([('id', '!=', rec.id), ('th_major_id', '=', rec.th_major_id.id), ('th_origin_id', '=', rec.th_origin_id.id)]) for rec in self):
            raise ValidationError(_("Ngành trên đã được thiết lập. Vui lòng kiểm tra lại!"))


class ThStatusDetail(models.Model):
    _name = "th.status.detail"
    _description = "Trạng thái chi tiết"

    name = fields.Char(string="Tên trạng thái", required=True)
    sequence = fields.Integer('Trình tự')
    th_description = fields.Text(string="Mô tả")
    th_status_category_id = fields.Many2one(comodel_name="th.status.category", string="Nhóm trạng thái", ondelete="cascade")
    th_type = fields.Selection(string="Loại", selection=[('crm', 'CRM'), ('srm', 'SRM'), ('prm', 'PRM'), ('tom', 'TOM'), ('trm', 'TRM'), ('apm', 'APM')],  related="th_status_category_id.th_type")

class ThStatusCategory(models.Model):
    _name = "th.status.category"
    _description = "Danh sách trạng thái"
    # _inherit = ['mail.thread', 'mail.activity.mixin']

    name = fields.Char(string="Nhóm trạng thái", required=True)
    sequence = fields.Integer('Trình tự')
    th_description = fields.Text(string="Mô tả")
    th_type = fields.Selection(string="Loại", selection=[('crm', 'CRM'), ('srm', 'SRM'), ('prm', 'PRM'), ('tom', 'TOM'), ('trm', 'TRM'), ('apm', 'APM')])
    th_status_detail_ids = fields.One2many(comodel_name="th.status.detail", inverse_name="th_status_category_id",string="Trang thái chi tiết")

    @api.constrains('name')
    def _check_name(self):
        for rec in self:
            if self.search_count([('name', '=', rec.name), ('id', '!=', rec.id), ('th_type', '=', rec.th_type)]) > 0:
                raise ValidationError("Nhóm trạng thái %s đã tồn tại!" % rec.name)
class ThOwnershipUnit(models.Model):
    _name = "th.ownership.unit"
    _description = "Đơn vị sở hữu"

    name = fields.Char(string="Tên sở hữu", required=True)
    th_description = fields.Text(string="Mô tả")
    th_partner_id = fields.Many2one(comodel_name="res.partner", string="Tên liên hệ")
    color = fields.Integer("Color Index", default=0)
    th_code = fields.Char("Mã đơn vị sở hữu", required=1)


class ThInfoChannel(models.Model):
    _name = "th.info.channel"
    _description = "Channel"

    name = fields.Char(string="Kênh", required=True)
    th_description = fields.Text(string="Mô tả")


class THSourceGroup(models.Model):
    _name = "th.source.group"
    _description = "Nhóm nguồn"

    name = fields.Char(string="Nhóm nguồn", required=True)
    th_description = fields.Text(string="Mô tả")

class ThAdmissionsStation(models.Model):
    _name = "th.admissions.station"
    _description = "Trạm tuyển sinh"

    name = fields.Char(string="Mã Trạm", required=True)
    th_name = fields.Char(string="Tên Trạm")
    th_description = fields.Text(string="Mô tả")

class ThAdmissionsRegion(models.Model):
    _name = "th.admissions.region"
    _description = "Vùng tuyển sinh"

    name = fields.Char(string="Vùng tuyển sinh", required=True)
    th_description = fields.Text(string="Mô tả")


class ThGraduationSystem(models.Model):
    _name = "th.graduation.system"
    _description = "Hệ tốt nghiệp"

    name = fields.Char(string="Mã hệ tốt nghiệp", required=True)
    th_description = fields.Char(string="Hệ tốt nghiệp", )


class ThCombinationOfSubjects(models.Model):
    _name = "th.combination.subjects"
    _description = "Tổ hợp môn"

    name = fields.Char(string="Tổ hợp môn", required=True)
    th_description = fields.Char(string="Mô tả", )