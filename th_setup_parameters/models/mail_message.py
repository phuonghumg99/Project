from odoo import fields, models, api
import xmlrpc.client
from markupsafe import Markup

class MailMessage(models.Model):
    _inherit = ['mail.message']

    th_aff_mail_message_id = fields.Integer(string="ID Mail message AFF", copy=False)

    @api.model
    def create(self, vals_list):
        res = super(MailMessage, self).create(vals_list)
        self.action_synchronized_mail_message(res)
        return res

    def action_synchronized_mail_message(self, res):
        server_api = self.env['th.api.server'].search([('state', '=', 'deploy'), ('th_type', '=', 'aff')], limit=1,
                                                      order='id desc')
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

        author_id = self.env['th.api.server'].search([('state', '=', 'deploy'), ('th_type', '=', 'aff')], limit=1, order='id desc').th_partner_api_id
        subtype_id = result_apis.execute_kw(db, uid_api, password, 'ir.model.data', 'search_read', [[['model', '=', 'mail.message.subtype'], ['name', '=', 'mt_note'], ['complete_name', '=', 'mail.mt_note']]], {'limit':1})[0]['res_id']
        if not subtype_id:
            return True
        for rec in res:
            res_id = False
            if rec.model == 'th.apm':
                res_id = self.env['th.apm'].search([('id', '=', rec.res_id)]).th_opportunity_aff_id
            if rec.model == 'crm.lead':
                res_id = self.env['crm.lead'].search([('id', '=', rec.res_id)]).th_lead_aff_id
            data_to_send = {
                'date': rec.date,
                'author_id': int(author_id),
                'message_type': 'comment',
                'subtype_id': subtype_id,
                'model': 'th.opportunity.ctv',
                'res_id': res_id,
                'body': Markup(rec.body),
            }
            try:
                res_id = result_apis.execute_kw(db, uid_api, password, 'mail.message', 'create', [data_to_send])
                rec.write({'th_aff_mail_message_id': res_id})
            except Exception as e:
                print(e)