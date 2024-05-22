from odoo import models, fields


class InvisibleLog(models.Model):
    _name = 'th.invisible.log'

    th_ir_model_id = fields.Many2one(string="", comodel_name="ir.model")

    def th_ir_model(self):
        return self.sudo().search([]).th_ir_model_id.mapped('model')
