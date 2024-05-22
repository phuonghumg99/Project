# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import xlrd
import base64
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class ImportPrmWizard(models.TransientModel):
    _name = 'th.import.prm'
    _description = 'Import'

    file = fields.Binary(string='Tải lên tập tin của bạn',)
    file_name = fields.Char()

    def action_import_data_prm(self):
        try:
            return self.import_prm()
        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise ValidationError(_("Đã xảy ra lỗi khi nhập PRM, vui lòng liên hệ với quản trị viên!"))

    def import_prm(self):
        wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.file))
        sheet = wb.sheet_by_index(0)
        start_row = 0
        header = False

        for i in range(start_row, sheet.nrows):
            row = sheet.row_values(i)
            if i == 0:
                header = row
            else:
                prm_data_list = {
                    "th_ownership_unit_id": self.env['th.ownership.unit'].search([('name', '=', row[0])]).id if row[0] else False,
                    "th_partner_id": self.env['res.partner'].search([('name', '=', row[1]), ('th_customer_code','=', row[19])]).id if row[1] else False,
                    "th_user_id": self.env['res.users'].search([('name', '=', row[2])]).id if row[2] else False,
                    "th_partner_phone": int(row[3]) if row[3] else False,
                    "th_partner_phone2": int(row[4]) if row[4] else False,
                    "th_partner_email": row[5] if row[5] else False,
                    "th_call_status": self.env['th.status.category'].search([('name', '=', row[6]), ('th_type', '=', 'prm')]).id if row[6] else False,
                    "th_call_status_detail_id": self.env['th.status.detail'].search([('name', '=', row[7]), ('th_type', '=', 'prm')]).id if row[7] else False,
                    "th_stage_id": self.env['prm.level'].search([('name', '=', row[8])]).id if row[8] else False,
                    "th_partner_group_ids": self.env['prm.partner.group'].search([('name', '=', row[9])]) if row[9] else False,
                    "th_last_check": datetime.strptime(row[10], '%d/%m/%Y %H:%M') if row[10] else False,
                    "th_partner_reference_id": self.env['res.partner'].search([('name', '=', row[11])]).id if row[11] else False,
                    "th_commission_policy": self.env['prm.commission.policy'].search([('name', '=', row[12])]).id if row[12] else False,
                    "th_partner_source_id": self.env['prm.partner.source'].search([('name', '=', row[13])]).id if row[13] else False,
                    "th_date_to_level_up_p4": datetime.strptime(row[14], '%d/%m/%Y') if row[14] else False,
                    "th_date_to_level_up_p5": datetime.strptime(row[15], '%d/%m/%Y') if row[15] else False,
                    "th_date_to_level_up_p6": datetime.strptime(row[16], '%d/%m/%Y') if row[16] else False,
                    "th_contract_number": int(row[17]) if row[17] else False,
                    "th_contract_sign_date": xlrd.xldate.xldate_as_datetime(row[18], wb.datemode) if row[18] else False,
                    "th_partner_code": row[19] if row[19] else False,
                    "th_collaborative_products_ids": [(6, 0, self.env['prm.collaborative.products'].search([('name', '=', row[20])]).ids)] if row[20] else False,
                    "th_description": row[21] if row[21] else False,
                    "th_data_getfly": [f'{header[i]}: {row[i]}' for i in range(header.index('Mô tả', 0) + 1, len(row))],

                }
                self.env['prm.lead'].create(prm_data_list)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }