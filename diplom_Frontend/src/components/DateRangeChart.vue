<template>
  <div class="date-range-chart">
    <div class="chart-container">
      <canvas ref="chartCanvas"></canvas>
    </div>
    
    <div class="chart-controls">
      <div class="selected-range">
        <span>Выбранный период:</span>
        <strong>{{ selectedRange.start }} - {{ selectedRange.end }}</strong>
      </div>
      <div class="chart-actions">
        <button @click="clearSelection" class="clear-selection-btn">Очистить выделение</button>
        <button @click="confirmSelection" class="confirm-btn" :disabled="!hasSelection">
          Применить диапазон
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, computed, watch } from 'vue'
import { Chart, registerables } from 'chart.js'
import 'chartjs-adapter-date-fns'
import { enUS } from 'date-fns/locale'

Chart.register(...registerables)

const props = defineProps({
  documents: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['range-selected'])

const chartCanvas = ref(null)
let chart = null
let isSelecting = false
let selectionStart = null

// Данные для графика
const chartData = computed(() => {
  if (!props.documents.length) return { dates: [], counts: [] }

  // Группируем документы по дате
  const dateCounts = {}
  props.documents.forEach(doc => {
    const date = doc.date
    dateCounts[date] = (dateCounts[date] || 0) + 1
  })

  // Сортируем даты
  const sortedDates = Object.keys(dateCounts).sort()
  
  return {
    dates: sortedDates,
    counts: sortedDates.map(date => dateCounts[date])
  }
})

// Выбранный диапазон
const selectedRange = ref({
  start: '',
  end: ''
})

const hasSelection = computed(() => selectedRange.value.start && selectedRange.value.end)

// Получаем индексы выбранных дат
const selectedDateIndices = computed(() => {
  if (!selectedRange.value.start || !selectedRange.value.end) return []
  
  const startDate = new Date(selectedRange.value.start)
  const endDate = new Date(selectedRange.value.end)
  
  return chartData.value.dates.reduce((indices, date, index) => {
    const currentDate = new Date(date)
    if (currentDate >= startDate && currentDate <= endDate) {
      indices.push(index)
    }
    return indices
  }, [])
})

// Пользовательский плагин для закрашивания фона выбранных областей
const selectionBackgroundPlugin = {
  id: 'selectionBackground',
  beforeDatasetsDraw(chart, args, options) {
    const { ctx } = chart
    const xAxis = chart.scales.x
    const yAxis = chart.scales.y
    
    if (selectedDateIndices.value.length === 0) return
    
    ctx.save()
    
    // Находим минимальный и максимальный индексы выбранных дат
    const minIndex = Math.min(...selectedDateIndices.value)
    const maxIndex = Math.max(...selectedDateIndices.value)
    
    // Получаем координаты для закрашивания
    const startPixel = xAxis.getPixelForValue(chartData.value.dates[minIndex])
    const endPixel = xAxis.getPixelForValue(chartData.value.dates[maxIndex])
    
    // Рассчитываем ширину столбца с учетом смещения
    const totalBars = chartData.value.dates.length
    const availableWidth = xAxis.width
    const barWidth = (availableWidth / totalBars) * 0.7
    
    // Закрашиваем область под выбранными столбцами
    ctx.fillStyle = 'rgba(52, 152, 219, 0.2)'
    ctx.fillRect(
      startPixel - barWidth, // Смещаем влево на полную ширину столбца
      yAxis.top,
      endPixel - startPixel + barWidth,
      yAxis.height
    )
    
    // Добавляем границу вокруг выделенной области
    ctx.strokeStyle = 'rgba(52, 152, 219, 0.8)'
    ctx.lineWidth = 2
    ctx.setLineDash([5, 5])
    ctx.strokeRect(
      startPixel - barWidth, // Смещаем влево на полную ширину столбца
      yAxis.top,
      endPixel - startPixel + barWidth,
      yAxis.height
    )
    
    ctx.restore()
  }
}

// Получаем индекс даты по координате X с учетом смещения
const getDateIndexFromX = (x) => {
  if (!chart) return -1
  
  const xAxis = chart.scales.x
  const totalBars = chartData.value.dates.length
  const availableWidth = xAxis.width
  const barWidth = (availableWidth / totalBars) * 0.7
  
  // Смещаем координату X вправо на половину ширины столбца
  const adjustedX = x + barWidth / 2
  
  const xValue = xAxis.getValueForPixel(adjustedX)
  if (!xValue) return -1
  
  const clickedDate = new Date(xValue).toISOString().split('T')[0]
  return chartData.value.dates.findIndex(date => date === clickedDate)
}

// Инициализация графика
const initChart = () => {
  if (!chartCanvas.value) return

  const ctx = chartCanvas.value.getContext('2d')
  
  const data = {
    labels: chartData.value.dates,
    datasets: [
      {
        label: 'Количество публикаций',
        data: chartData.value.counts,
        backgroundColor: (context) => {
          const index = context.dataIndex
          if (selectedDateIndices.value.includes(index)) {
            return 'rgba(231, 76, 60, 0.8)'
          }
          return 'rgba(54, 162, 235, 0.6)'
        },
        borderColor: (context) => {
          const index = context.dataIndex
          if (selectedDateIndices.value.includes(index)) {
            return 'rgba(231, 76, 60, 1)'
          }
          return 'rgba(54, 162, 235, 1)'
        },
        borderWidth: 2,
        borderRadius: 4,
        borderSkipped: false,
      }
    ]
  }

  const config = {
    type: 'bar',
    data: data,
    plugins: [selectionBackgroundPlugin],
    options: {
      responsive: true,
      maintainAspectRatio: false,
      interaction: {
        mode: 'nearest',
        intersect: true
      },
      plugins: {
        title: {
          display: true,
          text: 'Количество публикаций по дням',
          font: {
            size: 16
          }
        },
        tooltip: {
          backgroundColor: 'rgba(0, 0, 0, 0.8)',
          titleColor: '#fff',
          bodyColor: '#fff',
          borderColor: 'rgba(54, 162, 235, 1)',
          borderWidth: 1
        },
        legend: {
          display: false
        }
      },
      scales: {
        x: {
          type: 'time',
          time: {
            unit: 'day',
            displayFormats: {
              day: 'dd.MM.yyyy'
            }
          },
          title: {
            display: true,
            text: 'Дата'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          offset: true // Добавляем отступ для лучшего отображения
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Количество публикаций'
          },
          grid: {
            color: 'rgba(0, 0, 0, 0.1)'
          },
          ticks: {
            stepSize: 1
          }
        }
      },
      onHover: (event, elements) => {
        if (isSelecting) {
          event.native.target.style.cursor = 'crosshair'
        } else {
          event.native.target.style.cursor = elements.length > 0 ? 'pointer' : 'default'
        }
      },
      // Настройки для правильного позиционирования столбцов
      datasets: {
        bar: {
          categoryPercentage: 0.8,
          barPercentage: 0.9
        }
      }
    }
  }

  chart = new Chart(ctx, config)
  
  // Добавляем обработчики событий мыши
  addMouseHandlers()
}

// Добавление обработчиков мыши для выделения
const addMouseHandlers = () => {
  if (!chartCanvas.value) return
  
  const canvas = chartCanvas.value
  
  canvas.addEventListener('mousedown', handleMouseDown)
  canvas.addEventListener('mousemove', handleMouseMove)
  canvas.addEventListener('mouseup', handleMouseUp)
  canvas.addEventListener('mouseleave', handleMouseLeave)
}

// Обработка нажатия мыши
const handleMouseDown = (event) => {
  if (!chart) return
  
  isSelecting = true
  const x = event.offsetX
  selectionStart = x
  
  // Получаем индекс даты из координаты X с учетом смещения
  const startIndex = getDateIndexFromX(x)
  if (startIndex !== -1) {
    const clickedDate = chartData.value.dates[startIndex]
    selectedRange.value.start = clickedDate
    selectedRange.value.end = clickedDate
  }
  
  chartCanvas.value.style.cursor = 'crosshair'
  updateChart()
}

// Обработка движения мыши при выделении
const handleMouseMove = (event) => {
  if (!isSelecting || !selectionStart || !chart) return
  
  const x = event.offsetX
  
  // Получаем индексы дат из координат с учетом смещения
  const startIndex = getDateIndexFromX(selectionStart)
  const currentIndex = getDateIndexFromX(x)
  
  if (startIndex !== -1 && currentIndex !== -1) {
    // Определяем начальную и конечную даты
    const minIndex = Math.min(startIndex, currentIndex)
    const maxIndex = Math.max(startIndex, currentIndex)
    
    selectedRange.value.start = chartData.value.dates[minIndex]
    selectedRange.value.end = chartData.value.dates[maxIndex]
    
    updateChart()
  }
}

// Обработка отпускания мыши
const handleMouseUp = () => {
  isSelecting = false
  selectionStart = null
  if (chartCanvas.value) {
    chartCanvas.value.style.cursor = 'default'
  }
}

// Обработка выхода мыши за пределы canvas
const handleMouseLeave = () => {
  isSelecting = false
  selectionStart = null
  if (chartCanvas.value) {
    chartCanvas.value.style.cursor = 'default'
  }
}

// Обновление графика
const updateChart = () => {
  if (chart) {
    chart.update()
  }
}

// Очистка выделения
const clearSelection = () => {
  selectedRange.value.start = ''
  selectedRange.value.end = ''
  updateChart()
}

// Подтверждение выбора
const confirmSelection = () => {
  if (hasSelection.value) {
    emit('range-selected', {
      start: selectedRange.value.start,
      end: selectedRange.value.end
    })
  }
}

// Удаление обработчиков событий
const removeMouseHandlers = () => {
  if (!chartCanvas.value) return
  
  const canvas = chartCanvas.value
  
  canvas.removeEventListener('mousedown', handleMouseDown)
  canvas.removeEventListener('mousemove', handleMouseMove)
  canvas.removeEventListener('mouseup', handleMouseUp)
  canvas.removeEventListener('mouseleave', handleMouseLeave)
}

// Наблюдаем за изменениями в документах
watch(chartData, () => {
  if (chart) {
    removeMouseHandlers()
    chart.destroy()
    initChart()
  }
})

// Наблюдаем за изменениями выделения
watch(selectedDateIndices, () => {
  updateChart()
})

onMounted(() => {
  initChart()
})

onUnmounted(() => {
  removeMouseHandlers()
  if (chart) {
    chart.destroy()
  }
})
</script>

<style scoped>
.date-range-chart {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
}

.chart-container {
  position: relative;
  height: 400px;
  margin-bottom: 20px;
}

.chart-controls {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 5px;
}

.selected-range {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
}

.selected-range strong {
  color: #3498db;
  font-size: 16px;
}

.chart-actions {
  display: flex;
  gap: 10px;
}

.clear-selection-btn {
  background: #95a5a6;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.clear-selection-btn:hover {
  background: #7f8c8d;
}

.confirm-btn {
  background: #27ae60;
  color: white;
  border: none;
  padding: 8px 16px;
  border-radius: 5px;
  cursor: pointer;
  font-size: 14px;
}

.confirm-btn:disabled {
  background: #bdc3c7;
  cursor: not-allowed;
}

.confirm-btn:not(:disabled):hover {
  background: #219a52;
}

@media (max-width: 768px) {
  .chart-controls {
    flex-direction: column;
    align-items: stretch;
  }
  
  .selected-range {
    justify-content: center;
    text-align: center;
  }
  
  .chart-actions {
    justify-content: center;
  }
  
  .chart-container {
    height: 300px;
  }
}
</style>