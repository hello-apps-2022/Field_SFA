import frappe
from frappe.www.login import get_context as frappe_login_get_context

no_cache = True


def get_context(context):
	"""
	Companion context builder for the SFA login.html override.

	sfa_core/www/login.html overrides Frappe's core login page so it can patch
	login.login_handlers[200] and redirect SFA users to /sfa. But because the
	override shadows Frappe's own www/login.py, none of the template variables
	the page depends on ({{ logo }}, {{ app_name }}, {{ login_label }},
	provider_logins, signup_form_template, ldap_settings, etc.) get populated —
	so {{ logo }} renders empty/literal.

	Delegating to Frappe's original get_context rebuilds the full login context
	(logo, app_name, social/provider logins, signup form, LDAP settings, CSRF,
	disable_signup/disable_user_pass_login flags) exactly as the stock page
	expects, while our login.html keeps the /sfa redirect patch.
	"""
	frappe_login_get_context(context)

	# Inject SFA brand into the login template so it can show the tenant line,
	# the product mark, and the tagline. Falls back to FieldPro defaults.
	try:
		bs = frappe.get_cached_doc("SFA Brand Settings")
		context.sfa_brand = {
			"product_name": bs.product_name or "FieldPro",
			"tenant_name": bs.tenant_name or "",
			"tagline": bs.login_tagline or "",
			"mark": bs.logo_navbar or "/assets/sfa_core/images/fieldpro-mark.svg",
			"login_logo": "/assets/sfa_core/images/fieldpro-login.svg",
		}
	except Exception:
		context.sfa_brand = {
			"product_name": "FieldPro",
			"tenant_name": "",
			"tagline": "Know your field.",
			"mark": "/assets/sfa_core/images/fieldpro-mark.svg",
			"login_logo": "/assets/sfa_core/images/fieldpro-login.svg",
		}

	return context
