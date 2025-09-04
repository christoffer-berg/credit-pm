import { createClient } from './supabase'

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || ''

class ApiClient {
  private supabase = createClient()

  private async getAuthHeaders(): Promise<Record<string, string>> {
    console.log('ApiClient: Getting auth headers...')
    
    // For development, skip auth and just return basic headers
    if (process.env.NODE_ENV === 'development') {
      console.log('ApiClient: Development mode - skipping auth')
      return {
        'Content-Type': 'application/json',
      }
    }
    
    try {
      const { data: { session }, error } = await this.supabase.auth.getSession()
      console.log('ApiClient: Session status:', session ? 'has session' : 'no session', error ? `error: ${error.message}` : '')
      
      return {
        'Content-Type': 'application/json',
        ...(session?.access_token && {
          Authorization: `Bearer ${session.access_token}`,
        }),
      }
    } catch (error) {
      console.error('ApiClient: Error getting session:', error)
      return {
        'Content-Type': 'application/json',
      }
    }
  }

  private async request<T>(
    endpoint: string,
    options: RequestInit = {}
  ): Promise<T> {
    const url = `${API_BASE_URL}${endpoint}`
    console.log('ApiClient: Making request to:', url)
    const headers = await this.getAuthHeaders()

    const response = await fetch(url, {
      ...options,
      headers: {
        ...headers,
        ...options.headers,
      },
    })

    console.log('ApiClient: Response status:', response.status, response.statusText)

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      console.error('ApiClient: Error response:', errorData)
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    const result = await response.json()
    console.log('ApiClient: Request successful, data length:', result?.length || 'N/A')
    return result
  }

  // Cases
  async getCases() {
    console.log('ApiClient: Fetching cases...')
    try {
      const result = await this.request('/api/v1/cases')
      console.log('ApiClient: Got cases:', result?.length || 0)
      return result
    } catch (error) {
      console.error('ApiClient: Failed to fetch cases:', error)
      throw error
    }
  }

  async getCase(id: string) {
    return this.request(`/api/v1/cases/${id}`)
  }

  async createCase(data: { organization_number: string; title?: string }) {
    return this.request('/api/v1/cases', {
      method: 'POST',
      body: JSON.stringify(data),
    })
  }

  // Sections
  async getSections(caseId: string) {
    return this.request(`/api/v1/sections/${caseId}`)
  }

  async generateSection(caseId: string, sectionType: string) {
    return this.request(`/api/v1/sections/${caseId}/generate?section_type=${sectionType}`, {
      method: 'POST',
    })
  }

  async updateSection(sectionId: string, data: { user_content: string }) {
    return this.request(`/api/v1/sections/${sectionId}`, {
      method: 'PUT',
      body: JSON.stringify(data),
    })
  }

  // Companies
  async getCompanies() {
    return this.request('/api/v1/companies')
  }

  async getCompany(id: string) {
    return this.request(`/api/v1/companies/${id}`)
  }

  // Financials
  async uploadFinancials(companyId: string, file: File) {
    const formData = new FormData()
    formData.append('file', file)

    const { data: { session } } = await this.supabase.auth.getSession()
    
    const response = await fetch(`${API_BASE_URL}/api/v1/financials/${companyId}/upload`, {
      method: 'POST',
      headers: {
        ...(session?.access_token && {
          Authorization: `Bearer ${session.access_token}`,
        }),
      },
      body: formData,
    })

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}))
      throw new Error(errorData.detail || `HTTP ${response.status}`)
    }

    return response.json()
  }

  async getFinancials(companyId: string) {
    return this.request(`/api/v1/financials/${companyId}`)
  }

  // Export
  async exportDocument(caseId: string, format: 'word' | 'pdf'): Promise<Blob> {
    const { data: { session } } = await this.supabase.auth.getSession()
    
    const response = await fetch(`${API_BASE_URL}/api/v1/export/${caseId}/${format}`, {
      method: 'POST',
      headers: {
        ...(session?.access_token && {
          Authorization: `Bearer ${session.access_token}`,
        }),
      },
    })

    if (!response.ok) {
      throw new Error(`Export failed: ${response.status}`)
    }

    return response.blob()
  }

  // Audit
  async getCaseAuditTrail(caseId: string) {
    return this.request(`/api/v1/audit/cases/${caseId}/trail`)
  }

  async getSectionHistory(sectionId: string) {
    return this.request(`/api/v1/audit/sections/${sectionId}/history`)
  }

  async getAiUsageStats(startDate?: string, endDate?: string) {
    const params = new URLSearchParams()
    if (startDate) params.append('start_date', startDate)
    if (endDate) params.append('end_date', endDate)
    
    return this.request(`/api/v1/audit/stats/ai-usage?${params}`)
  }
}

export const apiClient = new ApiClient()