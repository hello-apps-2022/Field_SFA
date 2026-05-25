frappe.pages['sfa-form-templates'].on_page_load = function(wrapper) {
    var page = frappe.ui.make_app_page({
        parent: wrapper,
        title: 'Sfa Form Templates',
        single_column: true
    });
};