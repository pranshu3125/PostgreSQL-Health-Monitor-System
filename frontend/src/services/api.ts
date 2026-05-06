import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export const api = axios.create({
  baseURL: API_URL,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

export const authApi = {
  login: async (username: string, password: string) => {
    const formData = new FormData()
    formData.append('username', username)
    formData.append('password', password)
    const response = await api.post('/api/auth/login', formData)
    return response.data
  },
  register: async (data: { email: string; username: string; password: string; full_name?: string }) => {
    const response = await api.post('/api/auth/register', data)
    return response.data
  },
}

export const usersApi = {
  getAll: async () => {
    const response = await api.get('/api/users')
    return response.data
  },
  getMe: async () => {
    const response = await api.get('/api/users/me')
    return response.data
  },
}

export const databasesApi = {
  getAll: async () => {
    const response = await api.get('/api/databases')
    return response.data
  },
  create: async (data: any) => {
    const response = await api.post('/api/databases', data)
    return response.data
  },
  test: async (data: any) => {
    const response = await api.post('/api/databases/test', data)
    return response.data
  },
  delete: async (id: number) => {
    const response = await api.delete(`/api/databases/${id}`)
    return response.data
  },
}

export const metricsApi = {
  getCurrent: async () => {
    const response = await api.get('/api/metrics/current')
    return response.data
  },
  getDefinitions: async () => {
    const response = await api.get('/api/metrics/definitions')
    return response.data
  },
}

export const alertsApi = {
  getAll: async () => {
    const response = await api.get('/api/alerts')
    return response.data
  },
  getRules: async () => {
    const response = await api.get('/api/alerts/rules')
    return response.data
  },
  createRule: async (data: any) => {
    const response = await api.post('/api/alerts/rules', data)
    return response.data
  },
  getSummary: async () => {
    const response = await api.get('/api/alerts/stats/summary')
    return response.data
  },
}
