frappe.pages['sfa-dashboard'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'SFA Dashboard',
        single_column: true
    });

    // Mount Vue SFA Dashboard component
    var container = document.createElement('div');
    container.id = 'sfa-app';
    container.innerHTML = '<sfa-dashboard></sfa-dashboard>';
    page.main.append(container);

    // Wait for SFA bundle to be available
    frappe.require('/assets/sfa_core/dist/sfa_desk.bundle.js', function() {
        if (window.SFA_Core && window.SFA_Core.mount) {
            window.SFA_Core.mount('#sfa-app');
        }
    });
};
