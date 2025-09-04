'use client'

import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CreateCaseDialog } from './create-case-dialog'
import { CaseList } from './case-list'
import { PlusCircle } from 'lucide-react'
import { apiClient } from '@/lib/api-client'

export function Dashboard() {
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [cases, setCases] = useState([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState(null)

  const fetchCases = async () => {
    console.log('Dashboard: Fetching cases...')
    setIsLoading(true)
    setError(null)
    
    try {
      // Try direct fetch first
      const response = await fetch('/api/v1/cases', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      })
      
      console.log('Dashboard: Response status:', response.status, response.statusText)
      
      if (response.ok) {
        const data = await response.json()
        console.log('Dashboard: SUCCESS! Got', data.length, 'cases')
        setCases(data)
      } else {
        throw new Error(`HTTP ${response.status}`)
      }
    } catch (err) {
      console.error('Dashboard: Error fetching cases:', err)
      setError(err.message)
    } finally {
      setIsLoading(false)
    }
  }

  useEffect(() => {
    console.log('Dashboard: useEffect running, calling fetchCases...')
    fetchCases()
  }, [])

  const refetch = () => {
    fetchCases()
  }

  console.log('Dashboard: isLoading:', isLoading, 'cases:', cases?.length || 0, 'error:', error)

  const handleCaseCreated = () => {
    setShowCreateDialog(false)
    refetch()
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">
              Credit PM Generator
            </h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-500">
                Development Mode
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Credit Memos</h2>
            <Button onClick={() => setShowCreateDialog(true)}>
              <PlusCircle className="w-4 h-4 mr-2" />
              New PM
            </Button>
          </div>

          {error ? (
            <Card>
              <CardHeader>
                <CardTitle>Error Loading Cases</CardTitle>
                <CardDescription className="text-red-600">
                  {error instanceof Error ? error.message : 'An error occurred'}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={() => refetch()}>
                  Try Again
                </Button>
              </CardContent>
            </Card>
          ) : isLoading ? (
            <div className="text-center py-8">Loading cases...</div>
          ) : cases && Array.isArray(cases) && cases.length > 0 ? (
            <CaseList cases={cases} onRefetch={refetch} />
          ) : (
            <Card>
              <CardHeader>
                <CardTitle>No Credit Memos</CardTitle>
                <CardDescription>
                  Get started by creating your first credit memo
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={() => setShowCreateDialog(true)}>
                  <PlusCircle className="w-4 h-4 mr-2" />
                  Create First PM
                </Button>
              </CardContent>
            </Card>
          )}
        </div>
      </main>

      <CreateCaseDialog
        open={showCreateDialog}
        onOpenChange={setShowCreateDialog}
        onCaseCreated={handleCaseCreated}
      />
    </div>
  )
}