import { ref, computed } from 'vue';

/**
 * Composable: useFrappeAPI
 * Reactive Frappe API client for Vue 3 components
 */
export function useFrappeAPI() {
    const loading = ref(false);
    const error = ref(null);

    async function call(method, args = {}, options = {}) {
        loading.value = true;
        error.value = null;
        try {
            const response = await frappe.call({
                method,
                args,
                ...options
            });
            return response.message;
        } catch (err) {
            error.value = err;
            throw err;
        } finally {
            loading.value = false;
        }
    }

    async function getList(doctype, filters = {}, fields = ['*'], limit = 20, order_by = 'modified desc') {
        return call('frappe.client.get_list', {
            doctype,
            filters,
            fields,
            limit,
            order_by
        });
    }

    async function getDoc(doctype, name) {
        return call('frappe.client.get', { doctype, name });
    }

    async function insertDoc(doctype, doc) {
        return call('frappe.client.insert', { doc: { doctype, ...doc } });
    }

    async function updateDoc(doctype, name, fieldname, value) {
        return call('frappe.client.set_value', { doctype, name, fieldname, value });
    }

    async function deleteDoc(doctype, name) {
        return call('frappe.client.delete', { doctype, name });
    }

    return {
        loading,
        error,
        call,
        getList,
        getDoc,
        insertDoc,
        updateDoc,
        deleteDoc
    };
}

/**
 * Composable: useSFAData
 * SFA-specific data fetching with caching
 */
export function useSFAData() {
    const { loading, error, call, getList } = useFrappeAPI();
    const visits = ref([]);
    const orders = ref([]);
    const reps = ref([]);
    const customers = ref([]);
    const beatPlans = ref([]);
    const payments = ref([]);
    const leaderboard = ref([]);

    async function loadVisits(filters = {}, dateRange = null) {
        const f = { ...filters };
        if (dateRange) {
            f.visit_date = ['between', dateRange];
        }
        visits.value = await getList('SFA Visit', f, [
            'name', 'customer', 'rep', 'visit_date', 'status',
            'check_in_time', 'check_out_time', 'duration',
            'gps_accuracy', 'order_value', 'payment_collected'
        ], 50, 'visit_date desc');
        return visits.value;
    }

    async function loadOrders(filters = {}) {
        orders.value = await getList('Sales Order', filters, [
            'name', 'customer', 'transaction_date', 'status',
            'total_qty', 'grand_total', 'rep'
        ], 50, 'transaction_date desc');
        return orders.value;
    }

    async function loadReps() {
        reps.value = await call('sfa_core.api.dashboard.get_active_reps');
        return reps.value;
    }

    async function loadCustomers(filters = {}) {
        customers.value = await getList('Customer', filters, [
            'name', 'customer_name', 'territory', 'customer_group',
            'custom_sfa_status', 'custom_last_visit_date'
        ], 100);
        return customers.value;
    }

    async function loadBeatPlans() {
        beatPlans.value = await getList('SFA Beat Plan', {}, [
            'name', 'plan_name', 'territory', 'day_of_week',
            'status', 'route_distance_km'
        ], 50);
        return beatPlans.value;
    }

    async function loadPayments(filters = {}) {
        payments.value = await getList('SFA Payment', filters, [
            'name', 'customer', 'rep', 'payment_date', 'amount',
            'payment_mode', 'status'
        ], 50, 'payment_date desc');
        return payments.value;
    }

    async function loadLeaderboard(period = 'month') {
        leaderboard.value = await call('sfa_core.api.dashboard.get_leaderboard', { period });
        return leaderboard.value;
    }

    return {
        loading,
        error,
        visits,
        orders,
        reps,
        customers,
        beatPlans,
        payments,
        leaderboard,
        loadVisits,
        loadOrders,
        loadReps,
        loadCustomers,
        loadBeatPlans,
        loadPayments,
        loadLeaderboard
    };
}

/**
 * Composable: useRealtime
 * Socket.io-based real-time updates via Frappe realtime
 */
export function useRealtime() {
    const notifications = ref([]);

    function subscribe(event, handler) {
        if (frappe.realtime) {
            frappe.realtime.on(event, handler);
        }
    }

    function unsubscribe(event, handler) {
        if (frappe.realtime) {
            frappe.realtime.off(event, handler);
        }
    }

    function subscribeToVisits() {
        subscribe('sfa_visit_updated', (data) => {
            notifications.value.unshift({
                type: 'visit',
                title: `Visit ${data.status}`,
                message: `${data.customer} by ${data.rep}`,
                timestamp: new Date(),
                data
            });
        });
    }

    function subscribeToOrders() {
        subscribe('sfa_order_placed', (data) => {
            notifications.value.unshift({
                type: 'order',
                title: 'New Order',
                message: `${data.customer} - ${data.grand_total}`,
                timestamp: new Date(),
                data
            });
        });
    }

    function subscribeToPayments() {
        subscribe('sfa_payment_collected', (data) => {
            notifications.value.unshift({
                type: 'payment',
                title: 'Payment Collected',
                message: `${data.customer} - ${data.amount}`,
                timestamp: new Date(),
                data
            });
        });
    }

    return {
        notifications,
        subscribe,
        unsubscribe,
        subscribeToVisits,
        subscribeToOrders,
        subscribeToPayments
    };
}
