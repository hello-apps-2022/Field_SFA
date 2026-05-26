frappe.pages['sfa-form-templates'].on_page_load = function(wrapper) {
    frappe.set_route('sfa-dashboard');
    setTimeout(function() {
        if (window.SFA_Core && window.SFA_Core.router) {
            window.SFA_Core.router.push('/form-templates');
        }
    }, 300);
};
