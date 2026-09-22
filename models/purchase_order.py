from odoo import api, fields, models


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    destination = fields.Selection(
        selection=[
            ("stock", "Stock"),
            ("sale", "Venta"),
            ("sale_note", "Nota de Venta"),
        ],
        string="Destino",
        required=True,
        copy=True,
    )
    sale_note = fields.Char(
        string="Nota de Venta",
        copy=True,
    )

    @api.onchange("destination")
    def _onchange_destination(self):
        """Discard a sale note when its destination no longer supports it."""
        for order in self:
            if order.destination != "sale_note":
                order.sale_note = False


class PurchaseOrderLine(models.Model):
    _inherit = "purchase.order.line"

    sale_note = fields.Char(
        string="Nota de Venta",
        copy=True,
    )

    @api.onchange("order_id")
    def _onchange_order_id_sale_note(self):
        """Initialize new lines from the order while keeping the value editable."""
        for line in self:
            if line.order_id and not line.sale_note:
                line.sale_note = line.order_id.sale_note

    @api.model_create_multi
    def create(self, vals_list):
        """Also apply the header value to lines created outside the form view."""
        order_ids = {
            vals.get("order_id")
            for vals in vals_list
            if vals.get("order_id") and "sale_note" not in vals
        }
        notes_by_order = {
            order.id: order.sale_note
            for order in self.env["purchase.order"].browse(order_ids)
        }
        for vals in vals_list:
            if "sale_note" not in vals and vals.get("order_id"):
                vals["sale_note"] = notes_by_order.get(vals["order_id"])
        return super().create(vals_list)

