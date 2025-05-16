// Dashboard specific JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Initialize any dashboard-specific functionality
    initializeDashboard();
});

// Initialize dashboard
function initializeDashboard() {
    // Add any dashboard-specific event listeners here
    setupLogoutConfirmation();
}

// Setup logout confirmation
function setupLogoutConfirmation() {
    const logoutLinks = document.querySelectorAll('[data-action="logout"]');
    logoutLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            if (confirm('Are you sure you want to log out?')) {
                window.location.href = this.getAttribute('href');
            }
        });
    });
}

// Handle file uploads
async function handleFileUpload(fileInput) {
    const file = fileInput.files[0];
    if (!file) {
        showFlashMessage('error', 'Please select a file');
        return;
    }

    try {
        const formData = new FormData();
        formData.append('file', file);

        const response = await fetch('/api/local/upload', {
            method: 'POST',
            body: formData
        });

        await handleApiError(response);
        
        showFlashMessage('success', 'File uploaded successfully');
        // Refresh file list
        loadFiles();
    } catch (error) {
        showFlashMessage('error', error.message || 'Failed to upload file');
    }
}

// Load files list
async function loadFiles() {
    try {
        const response = await fetch('/api/local/files');
        const data = await handleApiError(response);
        
        const filesList = document.getElementById('filesList');
        if (!filesList) return;

        filesList.innerHTML = data.files.map(file => `
            <div class="file-item">
                <span class="file-name">${file.name}</span>
                <span class="file-size">${formatFileSize(file.size)}</span>
                <span class="file-date">${formatDate(file.uploaded_at)}</span>
                <button onclick="downloadFile('${file.name}')" class="file-action">Download</button>
                <button onclick="deleteFile('${file.name}')" class="file-action">Delete</button>
            </div>
        `).join('');
    } catch (error) {
        showFlashMessage('error', error.message || 'Failed to load files');
    }
}

// Download file
async function downloadFile(filename) {
    try {
        const response = await fetch(`/api/local/download/${filename}`);
        await handleApiError(response);
        
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        a.remove();
    } catch (error) {
        showFlashMessage('error', error.message || 'Failed to download file');
    }
}

// Delete file
async function deleteFile(filename) {
    if (!confirm('Are you sure you want to delete this file?')) return;

    try {
        const response = await fetch(`/api/local/delete/${filename}`, {
            method: 'DELETE'
        });
        await handleApiError(response);
        
        showFlashMessage('success', 'File deleted successfully');
        // Refresh file list
        loadFiles();
    } catch (error) {
        showFlashMessage('error', error.message || 'Failed to delete file');
    }
}
