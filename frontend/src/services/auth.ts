import api from './api'
import { User } from '../types'

export const authService = {
  login: async (email: string, password: string) => {
    const res = await api.post('/api/auth/login', { email, password })
    return res.data // { access_token, user }
  },
  logout: async () => api.post('/api/auth/logout'),
  me: async (): Promise<User> => {
    const res = await api.get('/api/auth/me')
    return res.data
  },
  getUsers: async () => {
    const res = await api.get('/api/auth/users')
    return res.data
  }
}
