<template>
  <div class="file-upload" :class="{ 'has-file': file }">
    <div 
      class="drop-zone"
      @dragover.prevent="handleDragOver"
      @dragleave="handleDragLeave"
      @drop.prevent="handleDrop"
      :class="{ 'dragover': isDragging }"
    >
      <input 
        type="file"
        ref="fileInput"
        @change="handleFileChange"
        accept=".txt,.doc,.docx,.md"
        hidden
      />
      
      <div class="upload-content" @click="triggerFileInput">
        <div class="upload-icon">
          <span v-if="!file">📁</span>
          <span v-else>✅</span>
        </div>
        
        <div class="upload-text">
          <h3 v-if="!file">{{ isDragging ? 'Отпустите файл здесь' : 'Перетащите файл или' }}</h3>
          <h3 v-else>{{ file.name }}</h3>
          
          <button 
            type="button" 
            class="browse-btn"
            @click.stop="triggerFileInput"
          >
            {{ file ? 'Изменить файл' : 'Выберите файл' }}
          </button>
          
          <p v-if="file" class="file-info">
            Размер: {{ formatFileSize(file.size) }}
          </p>
          <p v-else class="file-hint">
            Поддерживаются: .txt, .doc, .docx
          </p>
        </div>
      </div>
    </div>
    
    <div v-if="file" class="upload-actions">
      <button 
        @click="handleUpload"
        :disabled="loading"
        class="upload-btn primary"
      >
        <span v-if="!loading">🔬 Начать анализ</span>
        <span v-else>⏳ Анализ...</span>
      </button>
      
      <button 
        @click="clearFile"
        class="upload-btn secondary"
      >
        ❌ Отмена
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const props = defineProps({
  loading: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['file-selected', 'upload'])

const fileInput = ref(null)
const isDragging = ref(false)
const file = ref(null)

const triggerFileInput = () => {
  fileInput.value?.click()
}

const handleFileChange = (event) => {
  const selectedFile = event.target.files[0]
  if (selectedFile) {
    setFile(selectedFile)
  }
}

const handleDragOver = () => {
  isDragging.value = true
}

const handleDragLeave = () => {
  isDragging.value = false
}

const handleDrop = (event) => {
  isDragging.value = false
  const droppedFile = event.dataTransfer.files[0]
  if (droppedFile) {
    setFile(droppedFile)
  }
}

const setFile = (selectedFile) => {
  file.value = selectedFile
  emit('file-selected', selectedFile)
}

const handleUpload = () => {
  if (file.value) {
    emit('upload')
  }
}

const clearFile = () => {
  file.value = null
  if (fileInput.value) {
    fileInput.value.value = ''
  }
  emit('file-selected', null)
}

const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
</script>

<style scoped>
.file-upload {
  background: white;
  border-radius: 15px;
  padding: 25px;
  box-shadow: 0 5px 20px rgba(0,0,0,0.1);
  transition: all 0.3s ease;
}

.file-upload.has-file {
  box-shadow: 0 8px 30px rgba(102, 126, 234, 0.2);
}

.drop-zone {
  border: 3px dashed #e0e0e0;
  border-radius: 12px;
  padding: 40px 20px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.drop-zone.dragover {
  border-color: #667eea;
  background: rgba(102, 126, 234, 0.05);
  transform: translateY(-2px);
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 20px;
}

.upload-icon {
  font-size: 60px;
  color: #667eea;
}

.upload-text {
  text-align: center;
}

.upload-text h3 {
  color: #333;
  margin-bottom: 15px;
  font-size: 1.3rem;
}

.browse-btn {
  background: #667eea;
  color: white;
  border: none;
  padding: 12px 30px;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  margin-bottom: 10px;
}

.browse-btn:hover {
  background: #5a67d8;
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.file-info {
  color: #4CAF50;
  font-weight: 500;
  margin-top: 10px;
}

.file-hint {
  color: #888;
  font-size: 0.9rem;
  margin-top: 10px;
}

.upload-actions {
  display: flex;
  gap: 15px;
  margin-top: 25px;
}

.upload-btn {
  flex: 1;
  padding: 14px;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.upload-btn.primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.upload-btn.primary:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
}

.upload-btn.primary:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.upload-btn.secondary {
  background: #f5f5f5;
  color: #666;
}

.upload-btn.secondary:hover {
  background: #e0e0e0;
}

</style>