document.addEventListener('DOMContentLoaded', () => {
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const receiptsGallery = document.getElementById('receipts-gallery');
    const exportButton = document.getElementById('export-button');

    // Fetch and display receipts on page load
    fetchReceipts();

    // Handle form submission for file upload
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!fileInput.files[0]) {
            alert('Please select a file to upload.');
            return;
        }
        const formData = new FormData();
        formData.append('file', fileInput.files[0]);

        try {
            const response = await fetch('/upload/', {
                method: 'POST',
                body: formData
            });
            if (response.ok) {
                const data = await response.json();
                console.log('Upload successful:', data);
                fetchReceipts(); // Refresh the gallery
            } else {
                console.error('Upload failed');
            }
        } catch (error) {
            console.error('Error uploading file:', error);
        }
    });

    // Handle export to Excel
    exportButton.addEventListener('click', async () => {
        try {
            const response = await fetch('/export/');
            if (response.ok) {
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.style.display = 'none';
                a.href = url;
                a.download = 'receipts.xlsx';
                document.body.appendChild(a);
                a.click();
                window.URL.revokeObjectURL(url);
            } else {
                console.error('Export failed');
            }
        } catch (error) {
            console.error('Error exporting data:', error);
        }
    });

    // Function to fetch and display receipts
    async function fetchReceipts() {
        try {
            const response = await fetch('/receipts/');
            if (response.ok) {
                const receipts = await response.json();
                receiptsGallery.innerHTML = ''; // Clear existing content
                receipts.forEach(receipt => {
                    const receiptItem = document.createElement('div');
                    receiptItem.className = 'receipt-item';
                    receiptItem.innerHTML = `
                        <p><strong>Vendor:</strong> ${receipt.vendor}</p>
                        <p><strong>Date:</strong> ${receipt.date}</p>
                        <p><strong>Total:</strong> ${receipt.total_amount}</p>
                    `;
                    receiptsGallery.appendChild(receiptItem);
                });
            } else {
                console.error('Failed to fetch receipts');
            }
        } catch (error) {
            console.error('Error fetching receipts:', error);
        }
    }
});
