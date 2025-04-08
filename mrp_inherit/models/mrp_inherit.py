from odoo import fields, models, api, _


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(MrpProduction, self).create(vals_list)
        if res.move_raw_ids:
            res.action_confirm()
            res.button_plan()
            res.action_start()
        return res