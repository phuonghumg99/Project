# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
import xlrd
import base64
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class ImportTrmWizard(models.TransientModel):
    _name = 'th.import.trm'
    _description = 'Import'

    file = fields.Binary(string='Tải lên tập tin của bạn',)
    file_name = fields.Char()

    def action_import_data_trm(self):
        try:
            return self.import_trm()
        except ValidationError as e:
            raise ValidationError(e)
        except Exception as e:
            raise ValidationError(_("Đã xảy ra lỗi khi nhập TRM, vui lòng liên hệ với quản trị viên!"))

    def import_trm(self):
        wb = xlrd.open_workbook(file_contents=base64.decodebytes(self.file))
        sheet = wb.sheet_by_index(0)
        start_row = 0
        header = False

        for i in range(start_row, sheet.nrows):
            row = sheet.row_values(i)
            if i == 0:
                header = row
            else:
                source_ids = []
                channel_ids = []

                for i in row[9].split(","):
                    if not self.env['th.trm.source'].search([('name', '=', i)]):
                        source = self.env['th.trm.source'].create({
                            "name": i
                        })
                        source_ids.append(source.id)
                    else:
                        source_ids.append(self.env['th.trm.source'].search([('name', '=', i)]).id)

                for i in row[14].split(","):
                    if not self.env['th.trm.channel'].search([('name', '=', i)]):
                        channel = self.env['th.trm.channel'].create({
                            "name": i
                        })
                        channel_ids.append(channel.id)
                    else:
                        channel_ids.append(self.env['th.trm.channel'].search([('name', '=', i)]).id)

                trm_data_list = {
                    "name": row[0] if row[0] else False,
                    "th_partner_id": self.env['th.lecturer.profile'].search([('name', '=', row[1]), ('th_customer_code', '=', row[15])]).id if row[1] else False,
                    "th_user_id": self.env['res.users'].search([('name', '=', row[2])]).id if row[2] else False,
                    "th_trm_phone": int(row[3]) if row[3] else False,
                    "th_trm_phone2": int(row[4]) if row[4] else False,
                    "th_trm_email": row[5] if row[5] else False,
                    "th_call_status": self.env['th.status.category'].search([('name', '=', row[6]), ('th_type', '=', 'trm')]).id if row[6] else False,
                    "th_status_detail_id": self.env['th.status.detail'].search([('name', '=', row[7]), ('th_type', '=', 'trm')]).id if row[7] else False,
                    "stage_id": self.env['th.trm.stage'].search([('name', '=', row[8])]).id if row[8] else False,
                    "th_trm_source":  source_ids if row[9] else False,
                    "th_last_check": datetime.strptime(row[10], '%d/%m/%Y %H:%M') if row[10] else False,
                    "th_product": self.env['product.product'].search([('name', '=', row[11])]).id if row[11] else False,
                    "th_level_up_date": datetime.strptime(row[12], '%d/%m/%Y') if row[12] else False,
                    "th_partner_reference_id": self.env['res.partner'].search([('name', '=', row[13])]).id if row[13] else False,
                    "th_trm_channel": channel_ids if row[14] else False,
                    "th_customer_code": row[15] if row[15] else False,
                    "th_description": row[16] if row[16] else False,
                    "th_data_getfly": [f'{header[i]}: {row[i]}' for i in range(header.index('Mô tả', 0) + 1, len(row))],

                }
                self.env['th.trm.lead'].create(trm_data_list)

        return {
            'type': 'ir.actions.client',
            'tag': 'reload'
        }
