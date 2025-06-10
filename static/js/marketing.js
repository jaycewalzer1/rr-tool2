// Marketing specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize marketing page
    initializeMarketing();
    loadPDFs();
});

// Initialize marketing page
function initializeMarketing() {
    // Set up form submission
    const uploadForm = document.getElementById('uploadForm');
    if (uploadForm) {
        uploadForm.addEventListener('submit', handlePDFUpload);
    }
}

// Handle PDF upload
async function handlePDFUpload(e) {
    e.preventDefault();
    const fileInput = document.querySelector('input[type="file"][name="pdf"]');
    const file = fileInput.files[0];

    if (!file) {
        showFlashMessage('error', 'Please select a PDF file');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('pdf', file);

        const response = await fetch('/api/local/upload', {
            method: 'POST',
            body: formData
        });

        await handleApiError(response);
        
        showFlashMessage('success', 'PDF uploaded successfully');
        fileInput.value = '';
        loadPDFs();
    } catch (error) {
        showFlashMessage('error', error.message || 'Failed to upload PDF');
    }
}

// Load PDFs
async function loadPDFs() {
    try {
        const response = await fetch('/api/local/files');
        const data = await handleApiError(response);
        
        const pdfList = document.getElementById('pdfList');
        if (!pdfList) return;

        pdfList.innerHTML = data.files.map(file => `
            <div class="pdf-item">
                <span class="pdf-name">${file.name}</span>
                <span class="pdf-size">${formatFileSize(file.size)}</span>
                <span class="pdf-date">${formatDate(file.uploaded_at)}</span>
                <button onclick="deletePDF('${file.name}')" class="pdf-action">Delete</button>
            </div>
        `).join('');
    } catch (error) {
        showFlashMessage('error', error.message || 'Failed to load PDFs');
    }
}

// Delete PDF
async function deletePDF(filename) {
    if (!confirm('Are you sure you want to delete this PDF?')) return;

    try {
        const response = await fetch(`/api/local/delete/${filename}`, {
            method: 'DELETE'
        });
        await handleApiError(response);
        
        showFlashMessage('success', 'PDF deleted successfully');
        loadPDFs();
    } catch (error) {
        showFlashMessage('error', error.message || 'Failed to delete PDF');
    }
}
