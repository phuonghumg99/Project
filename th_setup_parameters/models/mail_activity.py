from odoo import models, fields

class MailActivity(models.Model):
    _inherit = "mail.activity"

    def action_done(self):
        if not self.res_model:
            return super().action_done()
        if self.res_model in ['prm.lead', 'pom.lead', 'th.trm.lead', 'th.apm']:
            self.env[self.res_model].browse(self.res_id).sudo().write({'th_last_check': fields.Datetime.now()})
        return super().action_done()

    def action_done_schedule_next(self):
        if not self.res_model:
            return super().action_done_schedule_next()
        if self.res_model in ['prm.lead', 'pom.lead', 'th.apm']:
            self.env[self.res_model].browse(self.res_id).sudo().write({'th_last_check': fields.Datetime.now() })
        return super().action_done_schedule_next()

    def action_close_dialog(self):
        if not self.res_model:
            return super().action_close_dialog()
        if self.res_model in []:
            self.env[self.res_model].browse(self.res_id).sudo().write({'th_last_check': fields.Datetime.now() })
        return super().action_close_dialog()