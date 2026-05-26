frappe.pages['sfa-visits'].on_page_load = function(wrapper) {
    // Redirect to the main SFA app at the visits route
    frappe.set_route('sfa-dashboard');
    // Once loaded, navigate to visits
    setTimeout(function() {
        if (window.SFA_Core && window.SFA_Core.router) {
            window.SFA_Core.router.push('/visits');
        }
    }, 300);
};
