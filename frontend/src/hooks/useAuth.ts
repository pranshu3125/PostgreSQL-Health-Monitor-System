import { createContext, useContext, useState, useEffect, ReactNode } from 'react'
import { authApi, usersApi } from '../services/api'

interface User {
  id: number
  email: string
  username: string
  full_name?: string
  role: string
}

interface AuthContextType {
  token: string | null
  user: User | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

const AuthContext = createContext<AuthContextType | null>(null)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'))
  const [user, setUser] = useState<User | null>(null)

  useEffect(() => {
    if (token) {
      usersApi.getMe()
        .then(setUser)
        .catch(() => logout())
    }
  }, [token])

  const login = async (username: string, password: string) => {
    const response = await authApi.login(username, password)
    localStorage.setItem('token', response.access_token)
    setToken(response.access_token)
    const userData = await usersApi.getMe()
    setUser(userData)
  }

  const logout = () => {
    localStorage.removeItem('token')
    setToken(null)
    setUser(null)
  }

  return (
    <AuthContext.Provider value={{ token, user, login, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}
