frappe.pages['sfa-dashboard'].on_page_load = function(wrapper) {
    // Full-screen SFA app - hide sidebar for clean UI like Frappe CRM
    frappe.ui.make_app_page({
        parent: wrapper,
        title: 'SFA',
        single_column: true
    });

    // Create mount container
    var $container = $('<div id="sfa-root" style="height: calc(100vh - 60px); overflow: auto;"></div>');
    $(wrapper).find('.page-content').html($container);

    // Load and mount Vue SPA
    frappe.require([
        '/assets/sfa_core/dist/sfa_desk.bundle.js',
        '/assets/sfa_core/dist/sfa_core.bundle.css'
    ], function() {
        if (window.SFA_Core && window.SFA_Core.mount) {
            window.SFA_Core.mount('#sfa-root');
        } else {
            $container.html('<p style="padding:20px;color:#888;">SFA app failed to load. Run: bench build --apps sfa_core</p>');
        }
    });
};

frappe.pages['sfa-dashboard'].on_page_show = function(wrapper) {
    // Restore router view on tab re-focus
    if (window.SFA_Core && window.SFA_Core.router) {
        // Router is already active, nothing to do
    }
};
