/**
 * API Client for Lattice Backend
 * Handles all communication with the FastAPI backend
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

/**
 * Fetch with authentication
 */
async function fetchWithAuth(url: string, options?: RequestInit) {
  const token = typeof window !== 'undefined' ? localStorage.getItem('access_token') : null
  
  // Debug: log token status
  if (typeof window !== 'undefined') {
    console.debug('🔑 Token for', url, ':', token ? `${token.substring(0, 20)}...` : 'NO TOKEN')
  }
  
  const response = await fetch(`${API_BASE_URL}${url}`, {
    ...options,
    headers: {
      ...options?.headers,
      ...(token && { 'Authorization': `Bearer ${token}` }),
      'Content-Type': 'application/json',
      'ngrok-skip-browser-warning': '69420',
    },
  })
  
  // Handle authentication failures (401 or 403 without token)
  if (response.status === 401 || (response.status === 403 && !token)) {
    // Token expired, invalid, or missing
    console.debug('🚫', response.status, 'Unauthorized - redirecting to /login')
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
  }
  
  return response
}

export interface AuthToken {
  access_token: string
  token_type: string
}

/**
 * API Client
 */
export const api = {
  // ============= Authentication =============
  
  async signup(email: string, password: string, name: string): Promise<AuthToken> {
    const response = await fetch(`${API_BASE_URL}/api/auth/signup`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': '69420',
      },
      body: JSON.stringify({ email, password, name }),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Signup failed')
    }
    
    const data = await response.json()
    return data as AuthToken
  },
  
  async login(email: string, password: string): Promise<AuthToken> {
    const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
      method: 'POST',
      headers: { 
        'Content-Type': 'application/json',
        'ngrok-skip-browser-warning': '69420',
      },
      body: JSON.stringify({ email, password }),
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.detail || 'Login failed')
    }
    
    const data = await response.json()
    return data as AuthToken
  },
  
  async getSession() {
    const response = await fetchWithAuth('/api/auth/session', { method: 'POST' })
    
    if (!response.ok) {
      throw new Error('Failed to get session')
    }
    
    return response.json()
  },
  
  async getCurrentUser() {
    const response = await fetchWithAuth('/api/auth/me')
    
    if (!response.ok) {
      throw new Error('Failed to get user')
    }
    
    return response.json()
  },
  
  async logout() {
    if (typeof window !== 'undefined') {
      localStorage.removeItem('access_token')
    }
    return { success: true }
  },
  
  // ============= Onboarding (Knot Integration) =============
  
  async startOnboarding(email: string, phone?: string, testMode?: boolean) {
    try {
      const response = await fetchWithAuth('/api/onboarding/start', {
        method: 'POST',
        body: JSON.stringify({ email, phone, test_mode: testMode }),
      })
      
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          throw new Error('Not authenticated')
        }
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to start onboarding')
      }
      
      return response.json()
    } catch (error) {
      console.error('Start onboarding error:', error)
      throw error
    }
  },
  
  async completeOnboarding(sessionId: string) {
    try {
      const response = await fetchWithAuth('/api/onboarding/complete', {
        method: 'POST',
        body: JSON.stringify({ session_id: sessionId }),
      })
      
      if (!response.ok) {
        if (response.status === 401 || response.status === 403) {
          throw new Error('Not authenticated')
        }
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to complete onboarding')
      }
      
      return response.json()
    } catch (error) {
      console.error('Complete onboarding error:', error)
      throw error
    }
  },
  
  // ============= Chats =============
  
  async getChats() {
    try {
    const response = await fetchWithAuth('/api/chats')
    
    if (!response.ok) {
        // Don't throw error for 401/403, let fetchWithAuth handle redirect
        if (response.status === 401 || response.status === 403) {
          return []
        }
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to fetch chats')
    }
    
    return response.json()
    } catch (error) {
      // If fetch itself failed (network error, etc), fail silently during redirect
      console.debug('getChats error:', error)
      return []
    }
  },
  
  async getChat(id: number) {
    try {
    const response = await fetchWithAuth(`/api/chats/${id}`)
    
    if (!response.ok) {
        // Don't throw error for 401/403, let fetchWithAuth handle redirect
        if (response.status === 401 || response.status === 403) {
          return { id, messages: [] }
        }
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || 'Failed to fetch chat')
    }
    
    return response.json()
    } catch (error) {
      // If fetch itself failed (network error, etc), fail silently during redirect
      console.debug('getChat error:', error)
      return { id, messages: [] }
    }
  },
  
  async sendMessage(chatId: number, content: string): Promise<SendMessageResponse> {
    const response = await fetchWithAuth(`/api/chats/${chatId}/messages`, {
      method: 'POST',
      body: JSON.stringify({ content, sender_type: 'user' }),
    })
    
    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        throw new Error('Not authenticated')
      }
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to send message')
    }
    
    return response.json()
  },
  
  // ============= Groups =============
  
  async getGroups() {
    const response = await fetchWithAuth('/api/groups')
    
    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        return []
      }
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to fetch groups')
    }
    
    return response.json()
  },
  
  async getGroup(id: number) {
    const response = await fetchWithAuth(`/api/groups/${id}`)
    
    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        return { id, name: '', members: [] }
      }
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to fetch group')
    }
    
    return response.json()
  },
  
  async createGroup(name: string, members: string[]) {
    const response = await fetchWithAuth('/api/groups', {
      method: 'POST',
      body: JSON.stringify({ name, members }),
    })
    
    if (!response.ok) {
      throw new Error('Failed to create group')
    }
    
    return response.json()
  },
  
  // ============= Accounts =============
  
  async getAccounts() {
    const response = await fetchWithAuth('/api/accounts')
    
    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        return { accounts: [], total: 0, sandbox_mode: true }
      }
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to fetch accounts')
    }
    
    return response.json()
  },
  
  async getAccountsStatus() {
    const response = await fetchWithAuth('/api/accounts/status')
    
    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        return { connected: false, total: 0 }
      }
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to fetch account status')
    }
    
    return response.json()
  },
  
  async deleteAccount(accountId: number) {
    const response = await fetchWithAuth(`/api/accounts/${accountId}`, {
      method: 'DELETE',
    })
    
    if (!response.ok) {
      throw new Error('Failed to delete account')
    }
    
    return response.json()
  },

  // ============= Transactions =============

  async syncTransactions(merchantId?: string, limit: number = 100) {
    const params = new URLSearchParams()
    if (merchantId) params.set('merchant_id', merchantId)
    params.set('limit', limit.toString())
    
    const response = await fetchWithAuth(`/api/transactions/sync?${params}`)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to sync transactions')
    }
    
    return response.json()
  },

  async getTransactions(merchantId?: string, limit: number = 100) {
    const params = new URLSearchParams()
    if (merchantId) params.set('merchant_id', merchantId)
    params.set('limit', limit.toString())
    
    const response = await fetchWithAuth(`/api/transactions?${params}`)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to fetch transactions')
    }
    
    return response.json()
  },

  async getTransactionDetails(transactionId: string) {
    const response = await fetchWithAuth(`/api/transactions/${transactionId}`)
    
    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to fetch transaction details')
    }
    
    return response.json()
  },
  
  // ============= Insights =============
  
  async getInsights() {
    const response = await fetchWithAuth('/api/insights')
    
    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        return []
      }
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to fetch insights')
    }
    
    return response.json()
  },
  
  async getMonthlySummary() {
    const response = await fetchWithAuth('/api/insights/summary')
    
    if (!response.ok) {
      throw new Error('Failed to fetch monthly summary')
    }
    
    return response.json()
  },
  
  // ============= Settings =============
  
  async getSettings() {
    const response = await fetchWithAuth('/api/settings')
    
    if (!response.ok) {
      if (response.status === 401 || response.status === 403) {
        return {}
      }
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || 'Failed to fetch settings')
    }
    
    return response.json()
  },
  
  async updateSettings(section: string, data: any) {
    const response = await fetchWithAuth('/api/settings', {
      method: 'PATCH',
      body: JSON.stringify({ section, data }),
    })
    
    if (!response.ok) {
      throw new Error('Failed to update settings')
    }
    
    return response.json()
  },
}

// ============= Types =============

export interface User {
  id: number
  name: string
  email: string
  onboarding_status: string
}

export interface Message {
  id: number
  chat_id: number
  sender_id: number | null
  sender_type: 'user' | 'ai'
  content: string
  thinking?: string[]
  action?: 'card' | 'split' | 'tracker' | null
  drawer_data?: any
  created_at: string
}

export interface Chat {
  id: number
  type: 'solo' | 'group'
  title: string
  last_message?: string
  updated_at: string
  messages?: Message[]
}

export interface SendMessageResponse {
  user_message: Message
  ai_message?: Message | null
}

export interface Group {
  id: number
  name: string
  members: Array<{
    id: number
    name: string
    email: string
    role: string
  }>
  total_spend: number
  context: string
  last_activity: string
}

export interface Account {
  id: number
  user_id: number
  institution: string
  account_name: string
  account_type: string
  balance: number
  currency: string
  last_synced: string
  permissions: any
}

export interface Insight {
  id: string
  type: string
  title: string
  description: string
  impact: string
  date: string
  action?: string
}

