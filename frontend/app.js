const API_BASE = window.location.origin.includes('localhost') ? 'http://localhost:8000' : '';

async function fetchData(endpoint) {
    const res = await fetch(`${API_BASE}${endpoint}`);
    return res.json();
}

async function postData(endpoint, params = {}) {
    const url = new URL(`${API_BASE}${endpoint}`);
    Object.keys(params).forEach(key => url.searchParams.append(key, params[key]));
    const res = await fetch(url, { method: 'POST' });
    return res.json();
}

// UI State
function showTab(tabId) {
    document.querySelectorAll('.tab-content').forEach(t => t.classList.add('hidden'));
    document.getElementById(tabId).classList.remove('hidden');
}

// Load Data
async function loadDashboard() {
    const stats = await fetchData('/dashboard/stats');
    document.getElementById('total-income').textContent = stats.total_income_month.toFixed(2);
    document.getElementById('total-expense').textContent = stats.total_expense_month.toFixed(2);

    const annualList = document.getElementById('annual-stats-list');
    annualList.innerHTML = stats.expense_details.map(ed => `
        <li>
            <strong>${ed.name}:</strong>
            Year Target: ${ed.spend_per_year_est.toFixed(2)} |
            To Date: ${ed.spend_to_date_year.toFixed(2)}
        </li>
    `).join('');

    const missed = await fetchData('/dashboard/missed-payments');
    const alertSection = document.getElementById('alerts');
    const missedList = document.getElementById('missed-payments-list');

    if (missed.length > 0) {
        alertSection.classList.remove('hidden');
        missedList.innerHTML = missed.map(m => `
            <div class="missed-payment">
                MISSING PAYMENT: ${m.name} (Expected Day: ${m.expected_day}, Amount: ${m.amount})
            </div>
        `).join('');
    } else {
        alertSection.classList.add('hidden');
    }
}

async function loadManagement() {
    const accounts = await fetchData('/accounts');
    const accList = document.getElementById('accounts-list');
    accList.innerHTML = accounts.map(a => `<li>${a.name} - Balance: ${a.balance.toFixed(2)}</li>`).join('');

    const importSelect = document.getElementById('import-account-select');
    const cardAccSelect = document.getElementById('card-acc-id');
    const selects = [importSelect, cardAccSelect];
    selects.forEach(s => {
        s.innerHTML = accounts.map(a => `<option value="${a.id}">${a.name}</option>`).join('');
    });

    const cards = await fetchData('/cards');
    const cardsList = document.getElementById('cards-list');
    cardsList.innerHTML = cards.map(c => `<li>${c.card_type} (${c.card_number}) - ${c.name_on_card}</li>`).join('');

    const groups = await fetchData('/expense-groups');
    const expGroupSelect = document.getElementById('exp-group-id');
    expGroupSelect.innerHTML = groups.map(g => `<option value="${g.id}">${g.name}</option>`).join('');

    const expenses = await fetchData('/expense-types');
    const expList = document.getElementById('expenses-list');
    expList.innerHTML = expenses.map(e => `<li>${e.name} (Day ${e.payment_day}) - Target: ${e.total_spend_target}</li>`).join('');
}

// Event Listeners
document.getElementById('account-form').onsubmit = async (e) => {
    e.preventDefault();
    await postData('/accounts', {
        name: document.getElementById('acc-name').value,
        balance: document.getElementById('acc-balance').value || 0
    });
    loadManagement();
};

document.getElementById('group-form').onsubmit = async (e) => {
    e.preventDefault();
    await postData('/expense-groups', { name: document.getElementById('group-name').value });
    loadManagement();
};

document.getElementById('card-form').onsubmit = async (e) => {
    e.preventDefault();
    await postData('/cards', {
        card_type: document.getElementById('card-type').value,
        name_on_card: document.getElementById('card-holder').value,
        card_number: document.getElementById('card-num').value,
        expiry_date: document.getElementById('card-expiry').value,
        account_id: document.getElementById('card-acc-id').value
    });
    loadManagement();
};

document.getElementById('expense-form').onsubmit = async (e) => {
    e.preventDefault();
    await postData('/expense-types', {
        name: document.getElementById('exp-name').value,
        description1: document.getElementById('exp-desc1').value,
        description2: document.getElementById('exp-desc2').value,
        duration: document.getElementById('exp-duration').value || -1,
        payment_day: document.getElementById('exp-day').value,
        total_spend_target: document.getElementById('exp-target').value,
        group_id: document.getElementById('exp-group-id').value
    });
    loadManagement();
};

document.getElementById('import-form').onsubmit = async (e) => {
    e.preventDefault();
    const accountId = document.getElementById('import-account-select').value;
    const fileInput = document.getElementById('statement-file');
    if (!fileInput.files[0]) return;

    const formData = new FormData();
    formData.append('file', fileInput.files[0]);

    const res = await fetch(`${API_BASE}/import-statement/${accountId}`, {
        method: 'POST',
        body: formData
    });
    const result = await res.json();
    alert(result.message || result.detail);
    loadDashboard();
};

function exportData() {
    window.location.href = `${API_BASE}/export`;
}

// Init
loadDashboard();
loadManagement();
