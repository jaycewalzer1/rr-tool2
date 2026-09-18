// Dashboard behaviour: logout confirmation and the S3-backed file manager.

document.addEventListener('DOMContentLoaded', () => {
    setupLogoutConfirmation();
    setupFileManager();
});

function setupLogoutConfirmation() {
    document.querySelectorAll('[data-action="logout"]').forEach(link => {
        link.addEventListener('click', event => {
            event.preventDefault();
            if (confirm('Are you sure you want to log out?')) {
                window.location.href = link.getAttribute('href');
            }
        });
    });
}

function setupFileManager() {
    const dropZone = document.getElementById('drop-zone');
    const fileInput = document.getElementById('fileInput');
    if (!dropZone || !fileInput) return;

    dropZone.addEventListener('dragover', event => {
        event.preventDefault();
        dropZone.classList.add('dragover');
    });

    dropZone.addEventListener('dragleave', () => dropZone.classList.remove('dragover'));

    dropZone.addEventListener('drop', event => {
        event.preventDefault();
        dropZone.classList.remove('dragover');
        const file = event.dataTransfer.files[0];
        if (file) uploadFile(file);
    });

    fileInput.addEventListener('change', () => {
        const file = fileInput.files[0];
        if (file) uploadFile(file);
        fileInput.value = '';
    });

    loadFiles();
}

function setBusy(isBusy) {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = isBusy ? 'flex' : 'none';
}

async function postJson(url, body, method = 'POST') {
    const response = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body)
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) throw new Error(data.error || 'Request failed');
    return data;
}

// Three steps: ask the server for a presigned URL, PUT the file straight to S3,
// then tell the server to run the OCR pipeline over it.
async function uploadFile(file) {
    setBusy(true);
    try {
        const { upload_url: uploadUrl, filename } = await postJson(
            '/api/s3/upload-url', { filename: file.name }
        );

        const upload = await fetch(uploadUrl, {
            method: 'PUT',
            headers: { 'Content-Type': file.type },
            body: file
        });
        if (!upload.ok) throw new Error('Upload to storage failed');

        const result = await postJson('/api/s3/files', { filename });
        showFlashMessage('success', `Processed ${filename} (${result.rows_added} rows added)`);
        await loadFiles();
    } catch (error) {
        showFlashMessage('error', error.message || 'Upload failed');
    } finally {
        setBusy(false);
    }
}

async function loadFiles() {
    const filesList = document.getElementById('filesList');
    if (!filesList) return;

    try {
        const response = await fetch('/api/s3/files');
        const { files } = await handleApiError(response).then(r => r.json());

        filesList.replaceChildren();
        if (!files.length) {
            const empty = document.createElement('p');
            empty.textContent = 'No rent rolls uploaded yet.';
            filesList.append(empty);
            return;
        }

        files.forEach(file => filesList.append(renderFileRow(file)));
    } catch (error) {
        showFlashMessage('error', error.message || 'Failed to load files');
    }
}

function renderFileRow(file) {
    const row = document.createElement('div');
    row.className = 'file-item';

    const link = document.createElement('a');
    link.href = file.public_url;
    link.textContent = file.filename;
    link.target = '_blank';
    link.rel = 'noopener noreferrer';

    const size = document.createElement('span');
    size.className = 'file-size';
    size.textContent = formatFileSize(file.size);

    const deleteButton = document.createElement('button');
    deleteButton.className = 'delete-button';
    deleteButton.type = 'button';
    deleteButton.setAttribute('aria-label', `Delete ${file.filename}`);
    deleteButton.textContent = '\u00d7';
    deleteButton.addEventListener('click', () => {
        if (confirm('Are you sure you want to delete this file?')) {
            deleteFile(file.s3_key);
        }
    });

    row.append(link, size, deleteButton);
    return row;
}

async function deleteFile(s3Key) {
    setBusy(true);
    try {
        await postJson('/api/s3/files', { s3_key: s3Key }, 'DELETE');
        showFlashMessage('success', 'File deleted');
        await loadFiles();
    } catch (error) {
        showFlashMessage('error', error.message || 'Failed to delete file');
    } finally {
        setBusy(false);
    }
}
