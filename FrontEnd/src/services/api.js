import axios from 'axios'

const API_BASE_URL = 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
})
export const analyzeDocument = async (formData) => {
  const response = await axios.post(`${API_BASE_URL}/api/analyze/`, formData, {
    headers: {
      'Content-Type': 'multipart/form-data'
    }
  })
  return response
}

export default api