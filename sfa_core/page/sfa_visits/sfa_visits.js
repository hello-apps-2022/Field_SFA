frappe.pages['sfa-visits'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'SFA Visits',
        single_column: true
    });

    var container = document.createElement('div');
    container.id = 'sfa-visits-app';
    container.innerHTML = '<visits-list></visits-list>';
    page.main.append(container);

    frappe.require('/assets/sfa_core/dist/sfa_desk.bundle.js', function() {
        if (window.SFA_Core && window.SFA_Core.mount) {
            window.SFA_Core.mount('#sfa-visits-app');
        }
    });
};
