// Intercept BEFORE page load — override Frappe's set_route to ignore SFA routes
var _frappe_set_route = frappe.set_route.bind(frappe);
frappe.set_route = function() {
    var args = Array.from(arguments);
    // If it's trying to route to '#' or a hash-only path, ignore it
    var route = args[0];
    if (route === '#' || (typeof route === 'string' && route.match(/^#\//))) {
        return Promise.resolve();
    }
    return _frappe_set_route.apply(frappe, args);
};

frappe.pages['sfa-dashboard'].on_page_load = function(wrapper) {
    // Hide desk chrome immediately
    $('.navbar').hide();
    $('.page-head').hide();
    $('body').css('overflow', 'hidden');

    // Remove any existing container
    $('#sfa-root').remove();

    var $container = $('<div id="sfa-root" style="position:fixed;top:0;left:0;right:0;bottom:0;#sfa-root-inner" style="position:absolute;inset:0;background:#f9fafb;overflow:hidden;"></div>');
    $('body').append($container);

    // Kill any open dialogs immediately and after a delay
    function killDialogs() {
        // Bootstrap modals
        $('.modal').each(function() {
            try { $(this).modal('hide'); } catch(e) {}
        });
        $('.modal-backdrop').remove();
        $('body').removeClass('modal-open').css('padding-right', '');
        // Frappe msgprint
        if (frappe.msg_dialog && frappe.msg_dialog.hide) {
            try { frappe.msg_dialog.hide(); } catch(e) {}
        }
    }
    killDialogs();

    frappe.require([
        '/assets/sfa_core/dist/sfa_core.bundle.css',
        '/assets/sfa_core/dist/sfa_desk.bundle.js'
    ], function() {
        killDialogs();
        var app = window.SFA_Core || window.SFA;
        if (app && app.mount) {
            app.mount('#sfa-root');
        }
        setTimeout(killDialogs, 200);
        setTimeout(killDialogs, 800);
    });
};

frappe.pages['sfa-dashboard'].on_page_show = function(wrapper) {
    $('#sfa-root').show();
    $('.navbar').hide();
    $('body').css('overflow', 'hidden');
};

frappe.pages['sfa-dashboard'].on_page_hide = function(wrapper) {
    $('.navbar').show();
    $('body').css('overflow', '').css('padding-right', '');
    $('#sfa-root').hide();
};

// Fix: add a style to ensure slide panels teleported to body render correctly
var style = document.createElement('style');
style.textContent = '#sfa-root { transform: none !important; }';
document.head.appendChild(style);
