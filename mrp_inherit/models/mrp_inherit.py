from odoo import fields, models, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(self,MrpProduction).create(vals_list)
        res.action_confirm()
        res.button_plan()
        res.action_start()
