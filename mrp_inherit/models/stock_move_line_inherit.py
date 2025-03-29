from odoo import fields, models, api


class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    x_quantity_free = fields.Float(string="Quantity ", compute="_compute_x_quantity", store=True, default=0.0)
    x_quantity_used = fields.Float(string="Quantity Used", compute="_compute_x_quantity", store=True, default=0.0)

    @api.depends('quantity','location_usage', 'location_dest_usage')
    def _compute_x_quantity(self):
        for rec in self:
            if (rec.location_usage in ['internal','transit']) and (rec.location_dest_usage not in ['internal','transit']):
                rec.x_quantity_used = rec.quantity
            elif (rec.location_usage not in ['internal','transit']) and (rec.location_dest_usage in ['internal','transit']):
                rec.x_quantity_free = rec.quantity
