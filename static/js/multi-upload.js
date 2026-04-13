/* 
═══════════════════════════════════════════════════════════════════════
multi-upload.js - 다중 이미지 업로드 기능
═══════════════════════════════════════════════════════════════════════
작성일: 2026-01-02
기능: 여러 장의 사진을 한 번에 쉽게 올리는 기능 + 미리보기
*/

class MultiImageUpload {
    constructor(inputElement, previewContainerId, options = {}) {
        this.input = inputElement;
        this.previewContainer = document.getElementById(previewContainerId);
        this.files = [];
        this.maxFiles = options.maxFiles || 10;
        this.maxFileSize = options.maxFileSize || 5 * 1024 * 1024; // 5MB
        this.acceptedTypes = options.acceptedTypes || ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];
        
        this.init();
    }

    init() {
        // 파일 선택 이벤트
        this.input.addEventListener('change', (e) => this.handleFiles(e.target.files));
        
        // 드래그 앤 드롭 기능
        if (this.previewContainer) {
            this.setupDragDrop();
        }
    }

    setupDragDrop() {
        ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
            this.previewContainer.addEventListener(eventName, (e) => {
                e.preventDefault();
                e.stopPropagation();
            });
        });

        ['dragenter', 'dragover'].forEach(eventName => {
            this.previewContainer.addEventListener(eventName, () => {
                this.previewContainer.classList.add('drag-over');
            });
        });

        ['dragleave', 'drop'].forEach(eventName => {
            this.previewContainer.addEventListener(eventName, () => {
                this.previewContainer.classList.remove('drag-over');
            });
        });

        this.previewContainer.addEventListener('drop', (e) => {
            const files = e.dataTransfer.files;
            this.handleFiles(files);
        });
    }

    handleFiles(fileList) {
        const filesArray = Array.from(fileList);
        
        // 파일 개수 체크
        if (this.files.length + filesArray.length > this.maxFiles) {
            alert(`최대 ${this.maxFiles}개의 이미지만 업로드할 수 있습니다.`);
            return;
        }

        filesArray.forEach(file => {
            // 파일 타입 체크
            if (!this.acceptedTypes.includes(file.type)) {
                alert(`${file.name}은(는) 지원하지 않는 파일 형식입니다.`);
                return;
            }

            // 파일 크기 체크
            if (file.size > this.maxFileSize) {
                alert(`${file.name}의 크기가 너무 큽니다. (최대 ${this.maxFileSize / 1024 / 1024}MB)`);
                return;
            }

            this.files.push(file);
            this.createPreview(file);
        });

        this.updateFileCount();
    }

    createPreview(file) {
        const reader = new FileReader();
        const index = this.files.length - 1;

        reader.onload = (e) => {
            const previewItem = document.createElement('div');
            previewItem.className = 'image-preview-item';
            previewItem.dataset.index = index;

            previewItem.innerHTML = `
                <img src="${e.target.result}" alt="Preview">
                <button type="button" class="remove-image" onclick="multiUpload.removeFile(${index})">
                    <span>✕</span>
                </button>
                <div class="image-info">
                    <span class="file-name">${file.name}</span>
                    <span class="file-size">${this.formatFileSize(file.size)}</span>
                </div>
            `;

            this.previewContainer.appendChild(previewItem);
        };

        reader.readAsDataURL(file);
    }

    removeFile(index) {
        this.files.splice(index, 1);
        
        // 미리보기 제거
        const previewItem = this.previewContainer.querySelector(`[data-index="${index}"]`);
        if (previewItem) {
            previewItem.remove();
        }

        // 인덱스 재조정
        this.reindexPreviews();
        this.updateFileCount();
    }

    reindexPreviews() {
        const previews = this.previewContainer.querySelectorAll('.image-preview-item');
        previews.forEach((preview, index) => {
            preview.dataset.index = index;
            const removeBtn = preview.querySelector('.remove-image');
            removeBtn.setAttribute('onclick', `multiUpload.removeFile(${index})`);
        });
    }

    updateFileCount() {
        const countElement = document.getElementById('fileCount');
        if (countElement) {
            countElement.textContent = `${this.files.length}/${this.maxFiles}`;
        }
    }

    formatFileSize(bytes) {
        if (bytes === 0) return '0 Bytes';
        const k = 1024;
        const sizes = ['Bytes', 'KB', 'MB'];
        const i = Math.floor(Math.log(bytes) / Math.log(k));
        return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
    }

    getFiles() {
        return this.files;
    }

    clear() {
        this.files = [];
        this.previewContainer.innerHTML = '';
        this.input.value = '';
        this.updateFileCount();
    }
}

// 전역 변수로 선언 (HTML에서 접근 가능)
let multiUpload;

// 페이지 로드 시 초기화 (사용 예시)
document.addEventListener('DOMContentLoaded', function() {
    const imageInput = document.getElementById('imageInput');
    const previewContainer = 'imagePreview';
    
    if (imageInput && document.getElementById(previewContainer)) {
        multiUpload = new MultiImageUpload(imageInput, previewContainer, {
            maxFiles: 10,
            maxFileSize: 5 * 1024 * 1024, // 5MB
            acceptedTypes: ['image/jpeg', 'image/png', 'image/gif', 'image/webp']
        });
    }
});
