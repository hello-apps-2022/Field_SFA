import frappe
from frappe.model.document import Document


class SFABrandSettings(Document):
	def on_update(self):
		sync_brand_to_frappe()


def sync_brand_to_frappe():
	bs = frappe.get_cached_doc("SFA Brand Settings")

	navbar_logo = bs.logo_navbar or bs.logo_login
	if navbar_logo:
		navbar = frappe.get_single("Navbar Settings")
		navbar.app_logo = navbar_logo
		navbar.save(ignore_permissions=True)

	web = frappe.get_single("Website Settings")
	if bs.logo_login:
		web.app_logo = bs.logo_login
	if bs.favicon:
		web.favicon = bs.favicon
	if bs.product_name:
		web.app_name = bs.product_name
	web.save(ignore_permissions=True)

	frappe.db.commit()
	frappe.clear_cache()
