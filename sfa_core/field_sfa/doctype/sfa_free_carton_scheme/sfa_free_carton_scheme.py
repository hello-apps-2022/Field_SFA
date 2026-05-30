import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import getdate


class SFAFreeCartonScheme(Document):
    def validate(self):
        if self.target_type == "Customer":
            self.territory = None
            if not self.customer:
                frappe.throw(_("Customer is required for a Customer-targeted scheme."))
        elif self.target_type == "Territory":
            self.customer = None
            if not self.territory:
                frappe.throw(_("Territory is required for a Territory-targeted scheme."))

        if (self.buy_qty or 0) <= 0:
            frappe.throw(_("Buy Qty must be greater than zero."))
        if (self.free_qty or 0) <= 0:
            frappe.throw(_("Free Qty must be greater than zero."))
        if self.valid_from and self.valid_to and getdate(self.valid_from) > getdate(self.valid_to):
            frappe.throw(_("Valid From cannot be after Valid To."))
