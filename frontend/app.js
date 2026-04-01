const API_BASE_URL = "http://localhost:8000";

const captureBtn = document.getElementById("capture-btn");
const fileInput = document.getElementById("file-input");
const processingMsg = document.getElementById("processing-msg");
const editForm = document.getElementById("edit-form");
const scanSection = document.getElementById("scan-section");
const receiptList = document.getElementById("receipt-list");
const exportBtn = document.getElementById("export-btn");

const vendorInput = document.getElementById("vendor");
const dateInput = document.getElementById("date");
const amountInput = document.getElementById("amount");
const vatInput = document.getElementById("vat");
const totalInput = document.getElementById("total");
const categoryInput = document.getElementById("category");

const saveBtn = document.getElementById("save-btn");
const cancelBtn = document.getElementById("cancel-btn");

// Initialization
document.addEventListener("DOMContentLoaded", fetchReceipts);

// Event Listeners
captureBtn.addEventListener("click", () => fileInput.click());

fileInput.addEventListener("change", async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // Show processing message
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
        amount: parseFloat(amountInput.value) || 0,
        vat: parseFloat(vatInput.value) || 0,
        total: parseFloat(totalInput.value) || 0,
        category: categoryInput.value,
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
    amountInput.value = data.amount || 0;
    vatInput.value = data.vat || 0;
    totalInput.value = data.total || 0;
    categoryInput.value = data.category || "Miscellaneous";
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
            date.textContent = r.date;

            const category = document.createElement("span");
            category.className = "receipt-category";
            category.textContent = r.category;

            info.appendChild(vendor);
            info.appendChild(date);
            info.appendChild(category);

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

async function deleteReceipt(id) {
    if (!confirm("Are you sure you want to delete this receipt?")) return;

    try {
        const response = await fetch(`${API_BASE_URL}/receipts/${id}`, { method: "DELETE" });
        if (!response.ok) throw new Error("Delete failed");
        fetchReceipts();
    } catch (error) {
        alert("Error: " + error.message);
    }
}
window.deleteReceipt = deleteReceipt;
