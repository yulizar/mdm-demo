import typing

from dateutil.relativedelta import relativedelta

from odoo import fields, models, api, _
from datetime import timedelta

from odoo.api import ValuesType
from odoo.tools import float_round
from pprint import pprint

class MrpProduction(models.Model):
    _inherit = 'mrp.production'

    move_raw_ids = fields.One2many(copy=True)
    # date_start = fields.Datetime(default=fields.Datetime.now())

    @api.model_create_multi
    def create(self, vals_list):
        res = super(MrpProduction,self).create(vals_list)
        date_start_user = res.date_start

        if res.move_raw_ids:
            res.action_confirm()
            res.button_plan()
            res.action_start()
            res.update({'date_start': date_start_user})
        # res._split_work_order(res)
        if res.workorder_ids:
            for wo in res.workorder_ids:
                if not wo.date_start:
                    wo.date_start = date_start_user
                wc_capacity = wo.workcenter_id.default_capacity
                wc_capacity = wc_capacity * wo.workcenter_id.resource_calendar_id.hours_per_day
                split_wo_count = wo.qty_remaining // wc_capacity
                remainder_wo = wo.qty_remaining % wc_capacity
                wo._compute_duration_expected()
                date_start = wo.date_start

                if remainder_wo > 0:
                    for _ in range(int(split_wo_count)):
                        date_start = date_start + timedelta(days=1)
                        new_wo = wo.copy()

                        new_wo.update({
                            'qty_remaining': wc_capacity,
                            'date_start': date_start,
                            # 'date_finished': date_finished,
                            'duration_expected': wo.workcenter_id.resource_calendar_id.hours_per_day * 60
                        })
                        new_wo._compute_duration_expected()

                        for comp in new_wo.move_raw_ids:
                            comp.date = date_start_user
                            for ml in comp:
                                print(ml.date)
                                ml.sudo().write({'date': date_start_user})
                                print(ml.date)

                    wo.update({
                        'qty_remaining':remainder_wo,
                        'duration_expected': float_round((remainder_wo / wc_capacity) *  wo.workcenter_id.resource_calendar_id.hours_per_day * 60, precision_digits=0, rounding_method='HALF-UP')
                    })
                    wo.date_finished = wo.date_start + relativedelta(minutes = wo.duration_expected)
                    for comp in wo.move_raw_ids:
                        comp.date = date_start_user
                        for ml in comp:
                            print(ml.date)
                            ml.sudo().write({'date': date_start_user})
                            print(ml.date)

                else:
                    for _ in range(int(split_wo_count-1)):
                        date_start = date_start + timedelta(days=1)
                        # date_finished = date_finished + timedelta(days=1)
                        new_wo = wo.copy()
                        new_wo.update({
                            'qty_remaining': wc_capacity,
                            'date_start': date_start,
                            # 'date_finished': date_finished,
                            'duration_expected': wo.workcenter_id.resource_calendar_id.hours_per_day * 60
                        })
                        new_wo._compute_duration_expected()

                        for comp in new_wo.move_raw_ids:
                            comp.date = date_start_user
                            for ml in comp:
                                print(ml.date)
                                ml.sudo().write({'date': date_start_user})
                                print(ml.date)

                    wo.update({
                        'qty_remaining': wc_capacity,
                        'duration_expected': float_round((remainder_wo / wc_capacity) *  wo.workcenter_id.resource_calendar_id.hours_per_day * 60, precision_digits=0, rounding_method='HALF-UP')
                    })
                    wo.date_finished = wo.date_start + relativedelta(minutes=wo.duration_expected)
                    for comp in wo.move_raw_ids:
                        comp.date = date_start_user
                        for ml in comp:
                            print(ml.date)
                            ml.sudo().write({'date': date_start_user})
                            print(ml.date)
                    # wo._compute_duration_expected()

        return res

    def write(self, vals):
        res = super(MrpProduction, self).write(vals)
        return res

    def _change_move_line_date(self):
        for production in self:
            print('masuk change date',production.date_start)
            for move in production.move_raw_ids:
                for ml in move:
                    print(ml.reference, ml.date)
                    ml.write({
                        'date': production.date_start
                    })
                    print(ml.date)

    @api.model
    def _get_default_date_start(self):
        print('date start', self.date_start)
        if self.env.context.get('default_date_deadline'):
            date_finished = fields.Datetime.to_datetime(self.env.context.get('default_date_deadline'))
            date_start = date_finished - relativedelta(hours=1)
            return date_start
        if not self.date_start:
            return fields.Datetime.now()
        return self.date_start


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


    # def copy(self, default=None):
    #     new_wos = super().copy(default)
    #
    #     for old_wo, new_wo in zip(self, new_wos):
    #         if old_wo.move_raw_ids:
    #             operations_mapping = {}

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    date = fields.Datetime(related='move_id.date')