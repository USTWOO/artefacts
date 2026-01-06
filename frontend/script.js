document.addEventListener('DOMContentLoaded', () => {
    // UI Elements
    const uploadForm = document.getElementById('upload-form');
    const fileInput = document.getElementById('file-input');
    const receiptsGallery = document.getElementById('receipts-gallery');
    const exportButton = document.getElementById('export-button');
    const scanButton = document.getElementById('scan-camera-button');
    const cameraView = document.getElementById('camera-view');
    const video = document.getElementById('camera-stream');
    const canvas = document.getElementById('camera-canvas');
    const captureButton = document.getElementById('capture-button');
    const cancelCameraButton = document.getElementById('cancel-camera-button');
    const editSection = document.getElementById('edit-section');
    const editForm = document.getElementById('edit-form');

    let stream = null;

    // Fetch and display receipts on page load
    fetchReceipts();

    // --- Camera Functionality ---
    scanButton.addEventListener('click', async () => {
        try {
            if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
                stream = await navigator.mediaDevices.getUserMedia({ video: { facingMode: 'environment' } });
                video.srcObject = stream;
                cameraView.classList.remove('hidden');
                uploadForm.classList.add('hidden');
            } else {
                alert('Your browser does not support camera access.');
            }
        } catch (error) {
            console.error('Error accessing camera:', error);
            alert('Could not access the camera. Please ensure you have given permission.');
        }
    });

    captureButton.addEventListener('click', () => {
        const context = canvas.getContext('2d');
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        context.drawImage(video, 0, 0, canvas.width, canvas.height);

        canvas.toBlob(blob => {
            const file = new File([blob], 'receipt.png', { type: 'image/png' });
            const dataTransfer = new DataTransfer();
            dataTransfer.items.add(file);
            fileInput.files = dataTransfer.files;
            stopCamera();
        }, 'image/png');
    });

    cancelCameraButton.addEventListener('click', stopCamera);

    function stopCamera() {
        if (stream) {
            stream.getTracks().forEach(track => track.stop());
            stream = null;
        }
        cameraView.classList.add('hidden');
        uploadForm.classList.remove('hidden');
    }

    // --- Form Submission & Data Handling ---
    uploadForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        if (!fileInput.files[0]) {
            alert('Please select or capture a receipt image.');
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
                populateEditForm(data);
                editSection.classList.remove('hidden');
            } else {
                console.error('Failed to process receipt');
                alert('Failed to extract data from the receipt.');
            }
        } catch (error) {
            console.error('Error processing receipt:', error);
        }
    });

    editForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(editForm);
        const receiptData = Object.fromEntries(formData.entries());

        try {
            const response = await fetch('/save/', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(receiptData)
            });

            if (response.ok) {
                // Reset UI
                editForm.reset();
                fileInput.value = '';
                editSection.classList.add('hidden');
                // Refresh gallery
                fetchReceipts();
            } else {
                console.error('Failed to save receipt');
                alert('There was an error saving the receipt.');
            }
        } catch (error) {
            console.error('Error saving receipt:', error);
        }
    });

    function populateEditForm(data) {
        document.getElementById('edit-vendor').value = data.vendor || '';
        document.getElementById('edit-date').value = data.date || '';
        document.getElementById('edit-amount').value = data.amount || 0;
        document.getElementById('edit-vat').value = data.vat || 0;
        document.getElementById('edit-total').value = data.total_amount || 0;
    }

    // --- Existing functions for fetching and exporting ---
    async function fetchReceipts() {
        try {
            const response = await fetch('/receipts/');
            if (response.ok) {
                const receipts = await response.json();
                receiptsGallery.innerHTML = '';
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
});
