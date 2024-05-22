import xmlrpc

from odoo import _, fields, models, api, exceptions
import json

class PRMTransformStage(models.TransientModel):
    _name = 'prm.transform.stage'
    _description = 'Chuyển mối quan hệ'

    th_stage_id = fields.Many2one(comodel_name="prm.level", string="Mối quan hệ")
    def action_transform_stage(self):
        active_ids = self._context.get('active_ids')
        model_name = self._context.get('model_name') or self._context.get('active_model')
        for active_id in active_ids:
            if model_name == 'prm.lead':
                if self.env['prm.lead'].browse(active_id).th_pom_lead_count != 0:
                    raise exceptions.ValidationError(_('Không thể chuyển mối quan hệ khi bản ghi đã tồn tại POM'))
                else:
                    self.env['prm.lead'].browse(active_id).th_stage_id = self.th_stage_id

            if model_name == 'pom.lead':
                self.env['pom.lead'].browse(active_id).th_stage_id = self.th_stage_id

