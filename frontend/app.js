const API_BASE_URL = window.location.protocol + "//" + window.location.hostname + ":8000";

// Register Service Worker for PWA
if ("serviceWorker" in navigator) {
    window.addEventListener("load", () => {
        navigator.serviceWorker.register("sw.js").catch(err => console.log("SW registration failed:", err));
    });
}

const captureBtn = document.getElementById("capture-btn");
const fileInput = document.getElementById("file-input");
const processingMsg = document.getElementById("processing-msg");
const editForm = document.getElementById("edit-form");
const scanSection = document.getElementById("scan-section");
const receiptList = document.getElementById("receipt-list");
const exportBtn = document.getElementById("export-btn");

const vendorInput = document.getElementById("vendor");
const dateInput = document.getElementById("date");
const subtotalInput = document.getElementById("subtotal");
const vatInput = document.getElementById("vat");
const totalInput = document.getElementById("total");
const categoryInput = document.getElementById("category");
const imagePreview = document.getElementById("scanned-image-preview");

const saveBtn = document.getElementById("save-btn");
const cancelBtn = document.getElementById("cancel-btn");

let currentImageData = null;

// Initialization
document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    fetchReceipts();
    fetchStats();
});

// Navigation / Tabs
function initTabs() {
    const tabBtns = document.querySelectorAll(".tab-btn");
    const views = document.querySelectorAll(".view");

    tabBtns.forEach(btn => {
        btn.addEventListener("click", () => {
            const targetTab = btn.getAttribute("data-tab");

            tabBtns.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            views.forEach(v => {
                v.style.display = v.id === `${targetTab}-view` ? "block" : "none";
            });

            if (targetTab === "history") fetchReceipts();
            if (targetTab === "stats") fetchStats();
        });
    });
}

// Event Listeners
captureBtn.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    processingMsg.style.display = "block";
    scanSection.style.display = "none";
    editForm.style.display = "none";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch(`${API_BASE_URL}/ocr`, {
            method: "POST",
            body: formData,
        });

        if (!response.ok) throw new Error("OCR failed");

        const data = await response.json();
        currentImageData = data.image_path;
        populateForm(data);

        processingMsg.style.display = "none";
        editForm.style.display = "block";
    } catch (error) {
        alert("Error: " + error.message);
        processingMsg.style.display = "none";
        scanSection.style.display = "block";
    }
});

saveBtn.addEventListener("click", async () => {
    const data = {
        vendor: vendorInput.value,
        date: dateInput.value,
        subtotal: parseFloat(subtotalInput.value) || 0,
        vat: parseFloat(vatInput.value) || 0,
        total: parseFloat(totalInput.value) || 0,
        category: categoryInput.value,
        image_path: currentImageData
    };

    try {
        const response = await fetch(`${API_BASE_URL}/save`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        if (!response.ok) throw new Error("Save failed");

        editForm.style.display = "none";
        scanSection.style.display = "block";
        fetchReceipts();
        fetchStats();
        alert("Saved successfully!");
    } catch (error) {
        alert("Error: " + error.message);
    }
});

cancelBtn.addEventListener("click", () => {
    editForm.style.display = "none";
    scanSection.style.display = "block";
});

exportBtn.addEventListener("click", async () => {
    window.location.href = `${API_BASE_URL}/export`;
});

// Helper Functions
function populateForm(data) {
    vendorInput.value = data.vendor || "Unknown";
    dateInput.value = data.date || "Unknown";
    subtotalInput.value = data.subtotal || 0;
    vatInput.value = data.vat || 0;
    totalInput.value = data.total || 0;
    categoryInput.value = data.category || "Miscellaneous";

    if (data.image_path) {
        imagePreview.innerHTML = `<img src="${API_BASE_URL}${data.image_path}" alt="Receipt">`;
    }
}

async function fetchReceipts() {
    try {
        const response = await fetch(`${API_BASE_URL}/receipts`);
        if (!response.ok) throw new Error("Failed to fetch receipts");
        const receipts = await response.json();

        receiptList.innerHTML = "";
        receipts.forEach(r => {
            const item = document.createElement("div");
            item.className = "receipt-item";

            const info = document.createElement("div");
            info.className = "receipt-info";

            const vendor = document.createElement("span");
            vendor.className = "receipt-vendor";
            vendor.textContent = r.vendor;

            const date = document.createElement("span");
            date.className = "receipt-date";
            date.textContent = `${r.date} (${r.category})`;

            const viewLink = document.createElement("a");
            viewLink.href = `${API_BASE_URL}${r.image_path}`;
            viewLink.target = "_blank";
            viewLink.textContent = "View Image";
            viewLink.style.fontSize = "0.8rem";
            viewLink.style.color = "#007aff";

            info.appendChild(vendor);
            info.appendChild(date);
            if (r.image_path) info.appendChild(viewLink);

            const amount = document.createElement("div");
            amount.className = "receipt-amount";
            amount.textContent = `$${r.total.toFixed(2)}`;

            const deleteBtn = document.createElement("button");
            deleteBtn.className = "delete-btn";
            deleteBtn.textContent = "🗑️";
            deleteBtn.onclick = () => deleteReceipt(r.id);

            item.appendChild(info);
            item.appendChild(amount);
            item.appendChild(deleteBtn);

            receiptList.appendChild(item);
        });
    } catch (error) {
        console.error("Error:", error);
    }
}

async function fetchStats() {
    try {
        // Fetch Monthly Stats
        const mRes = await fetch(`${API_BASE_URL}/stats/monthly`);
        const mStats = await mRes.json();
        const monthlyList = document.getElementById("monthly-stats-list");
        monthlyList.innerHTML = mStats.map(s => `
            <div class="stat-item">
                <span>${s.month}</span>
                <span>Exp: $${s.total_expense.toFixed(2)} | VAT: $${s.total_vat.toFixed(2)}</span>
            </div>
        `).join("") || "<p>No data yet.</p>";

        // Fetch Category Stats
        const cRes = await fetch(`${API_BASE_URL}/stats/category`);
        const cStats = await cRes.json();
        const categoryList = document.getElementById("category-stats-list");
        categoryList.innerHTML = cStats.map(s => `
            <div class="stat-item">
                <span>${s.category}</span>
                <span>Exp: $${s.total_expense.toFixed(2)} | VAT: $${s.total_vat.toFixed(2)}</span>
            </div>
        `).join("") || "<p>No data yet.</p>";

    } catch (error) {
        console.error("Error fetching stats:", error);
    }
}

async function deleteReceipt(id) {
    if (!confirm("Are you sure you want to delete this receipt?")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/receipts/${id}`, { method: "DELETE" });
        if (!response.ok) throw new Error("Delete failed");
        fetchReceipts();
        fetchStats();
    } catch (error) {
        alert("Error: " + error.message);
    }
}
window.deleteReceipt = deleteReceipt;
