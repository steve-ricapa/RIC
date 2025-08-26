/**
 * RIC - Reflective Instruction Coach
 * Main JavaScript functionality
 */

class RICApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.setupDragAndDrop();
        this.setupAutoRefresh();
    }

    setupEventListeners() {
        // File input change handler
        const fileInput = document.getElementById('audioFile');
        if (fileInput) {
            fileInput.addEventListener('change', this.handleFileSelect.bind(this));
        }

        // Form submission handler
        const uploadForm = document.getElementById('uploadForm');
        if (uploadForm) {
            uploadForm.addEventListener('submit', this.handleFormSubmit.bind(this));
        }
    }

    setupDragAndDrop() {
        const uploadArea = document.querySelector('.upload-area');
        if (!uploadArea) return;

        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, this.preventDefaults, false);
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.add('dragover');
            }, false);
        });

        ['dragleave', 'drop'].forEach(eventName => {
            uploadArea.addEventListener(eventName, () => {
                uploadArea.classList.remove('dragover');
            }, false);
        });

        uploadArea.addEventListener('drop', this.handleDrop.bind(this), false);
    }

    setupAutoRefresh() {
        // Auto-refresh for processing status
        const analysisStatus = document.querySelector('.badge');
        if (analysisStatus && analysisStatus.textContent.includes('Procesando')) {
            this.startStatusPolling();
        }
    }

    preventDefaults(e) {
        e.preventDefault();
        e.stopPropagation();
    }

    handleDrop(e) {
        const dt = e.dataTransfer;
        const files = dt.files;

        if (files.length > 0) {
            const file = files[0];
            if (this.isValidAudioFile(file)) {
                const fileInput = document.getElementById('audioFile');
                fileInput.files = files;
                this.displayFileInfo(file);
            } else {
                this.showError('Formato de archivo no válido. Por favor sube un archivo de audio.');
            }
        }
    }

    handleFileSelect(event) {
        const file = event.target.files[0];
        if (file) {
            this.displayFileInfo(file);
        }
    }

    handleFormSubmit(event) {
        const fileInput = document.getElementById('audioFile');
        const uploadBtn = document.getElementById('uploadBtn');

        if (!fileInput.files || fileInput.files.length === 0) {
            event.preventDefault();
            this.showError('Por favor selecciona un archivo de audio.');
            return;
        }

        const file = fileInput.files[0];
        if (!this.isValidAudioFile(file)) {
            event.preventDefault();
            this.showError('Formato de archivo no válido.');
            return;
        }

        if (file.size > 100 * 1024 * 1024) { // 100MB
            event.preventDefault();
            this.showError('El archivo es demasiado grande. Máximo 100MB.');
            return;
        }

        // Show loading state
        this.setLoadingState(uploadBtn, true);
    }

    displayFileInfo(file) {
        const fileInfo = document.getElementById('fileInfo');
        const fileName = document.getElementById('fileName');

        if (fileInfo && fileName) {
            fileName.textContent = `${file.name} (${this.formatFileSize(file.size)})`;
            fileInfo.classList.remove('d-none');
            
            // Update feather icons
            if (typeof feather !== 'undefined') {
                feather.replace();
            }
        }
    }

    isValidAudioFile(file) {
        const validTypes = ['audio/mp3', 'audio/mpeg', 'audio/wav', 'audio/x-wav', 'audio/m4a', 'audio/ogg', 'audio/flac'];
        const validExtensions = ['mp3', 'wav', 'm4a', 'ogg', 'flac'];
        
        const fileExtension = file.name.split('.').pop().toLowerCase();
        
        return validTypes.includes(file.type) || validExtensions.includes(fileExtension);
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB', 'GB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        
        return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
    }

    setLoadingState(button, loading) {
        if (!button) return;

        if (loading) {
            button.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Subiendo...';
            button.disabled = true;
        } else {
            button.innerHTML = '<i data-feather="upload" class="me-2"></i>Subir y Analizar';
            button.disabled = false;
            
            if (typeof feather !== 'undefined') {
                feather.replace();
            }
        }
    }

    showError(message) {
        // Create alert if it doesn't exist
        let alertContainer = document.querySelector('.alert-container');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.className = 'alert-container';
            document.querySelector('.container').prepend(alertContainer);
        }

        const alert = document.createElement('div');
        alert.className = 'alert alert-danger alert-dismissible fade show';
        alert.innerHTML = `
            <i data-feather="alert-circle" class="me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        alertContainer.appendChild(alert);

        if (typeof feather !== 'undefined') {
            feather.replace();
        }

        // Auto-dismiss after 5 seconds
        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    showSuccess(message) {
        // Similar to showError but with success styling
        let alertContainer = document.querySelector('.alert-container');
        if (!alertContainer) {
            alertContainer = document.createElement('div');
            alertContainer.className = 'alert-container';
            document.querySelector('.container').prepend(alertContainer);
        }

        const alert = document.createElement('div');
        alert.className = 'alert alert-success alert-dismissible fade show';
        alert.innerHTML = `
            <i data-feather="check-circle" class="me-2"></i>
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;

        alertContainer.appendChild(alert);

        if (typeof feather !== 'undefined') {
            feather.replace();
        }

        setTimeout(() => {
            if (alert.parentNode) {
                alert.remove();
            }
        }, 5000);
    }

    startStatusPolling() {
        const currentUrl = window.location.pathname;
        const analysisId = currentUrl.split('/').pop();
        
        if (!analysisId || isNaN(analysisId)) return;

        const pollInterval = setInterval(async () => {
            try {
                const response = await fetch(`/api/analysis/${analysisId}/status`);
                const data = await response.json();

                if (data.status === 'completed' || data.status === 'error') {
                    clearInterval(pollInterval);
                    window.location.reload();
                }
            } catch (error) {
                console.error('Status polling error:', error);
                clearInterval(pollInterval);
            }
        }, 5000); // Poll every 5 seconds

        // Stop polling after 10 minutes to prevent infinite requests
        setTimeout(() => {
            clearInterval(pollInterval);
        }, 600000);
    }
}

// Utility functions
const RICUtils = {
    formatDuration(seconds) {
        const minutes = Math.floor(seconds / 60);
        const remainingSeconds = Math.floor(seconds % 60);
        return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
    },

    getSpeedColor(wpm) {
        if (wpm < 120) return '#f59e0b'; // warning
        if (wpm > 160) return '#ef4444'; // danger
        return '#10b981'; // success
    },

    getScoreColor(score) {
        if (score >= 80) return '#10b981'; // success
        if (score >= 60) return '#f59e0b'; // warning
        return '#ef4444'; // danger
    },

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }
};

// Initialize the app when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    new RICApp();
});

// Export for potential use in other scripts
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { RICApp, RICUtils };
}
