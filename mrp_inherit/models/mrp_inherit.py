from odoo import fields, models, api, _
from datetime import timedelta

from odoo.tools import float_round


class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    @api.model_create_multi
    def create(self, vals_list):
        res = super(MrpProduction, self).create(vals_list)
        if res.move_raw_ids:
            res.action_confirm()
            res.button_plan()
            res.action_start()
        if res.workorder_ids:
            for wo in res.workorder_ids:
                wc_capacity = wo.workcenter_id.default_capacity
                wc_capacity = wc_capacity * wo.workcenter_id.resource_calendar_id.hours_per_day
                split_wo_count = wo.qty_remaining // wc_capacity
                remainder_wo = wo.qty_remaining % wc_capacity
                print(remainder_wo)
                date_start = wo.date_start
                date_finished = wo.date_finished
                if remainder_wo > 0:
                    for _ in range(int(split_wo_count)):
                        date_start = date_start + timedelta(days=1)
                        date_finished = date_finished + timedelta(days=1)
                        new_wo = wo.copy()
                        new_wo.update({
                            'qty_remaining': wc_capacity,
                            'date_start': date_start,
                            'date_finished': date_finished,
                        })

                    wo.update({ 'qty_remaining':remainder_wo })
                else:
                    for _ in range(int(split_wo_count-1)):
                        date_start = date_start + timedelta(days=1)
                        date_finished = date_finished + timedelta(days=1)
                        new_wo = wo.copy()
                        new_wo.update({
                            'qty_remaining': wc_capacity,
                            'date_start': date_start,
                            'date_finished': date_finished,
                        })

                    wo.update({'qty_remaining': wc_capacity})

        return res

class MrpWorkorder(models.Model):
    _inherit = 'mrp.workorder'

    qty_remaining = fields.Float(store=True)

    @api.depends('qty_production', 'qty_reported_from_previous_wo', 'qty_produced', 'production_id.product_uom_id')
    def _compute_qty_remaining(self):
        for wo in self:
            if wo.production_id.product_uom_id:
                if wo.qty_remaining > 0:
                    continue
                else:
                    wo.qty_remaining = max(
                    float_round(wo.qty_production - wo.qty_reported_from_previous_wo - wo.qty_produced,
                                precision_rounding=wo.production_id.product_uom_id.rounding), 0)
            else:
                wo.qty_remaining = 0