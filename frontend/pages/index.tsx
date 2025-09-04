import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { CreateCaseDialog } from '@/components/dashboard/create-case-dialog'
import { CaseList } from '@/components/dashboard/case-list'
import { PlusCircle } from 'lucide-react'

export default function HomePage() {
  const [showCreateDialog, setShowCreateDialog] = useState(false)
  const [cases, setCases] = useState([])
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState(null)

  const fetchCases = async () => {
    console.log('Dashboard: Fetching cases...')
    setIsLoading(true)
    setError(null)
    
    try {
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
    fetchCases()
  }, [])

  const refetch = () => {
    fetchCases()
  }

  const handleCaseCreated = () => {
    setShowCreateDialog(false)
    refetch()
  }

  console.log('Dashboard: isLoading:', isLoading, 'cases:', cases?.length || 0, 'error:', error)

  return (
    <div className="min-h-screen bg-gray-50">
      <header className="bg-white shadow">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-6">
            <h1 className="text-3xl font-bold text-gray-900">
              Credit PM Generator
            </h1>
            <div className="flex items-center space-x-4">
              <Button onClick={() => setShowCreateDialog(true)}>
                <PlusCircle className="w-4 h-4 mr-2" />
                New PM
              </Button>
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
                  {error}
                </CardDescription>
              </CardHeader>
              <CardContent>
                <Button onClick={() => refetch()}>
                  Try Again
                </Button>
              </CardContent>
            </Card>
          ) : cases && Array.isArray(cases) && cases.length > 0 ? (
            <Card>
              <CardHeader>
                <CardTitle>Credit Memos ({cases.length})</CardTitle>
              </CardHeader>
              <CardContent>
                <CaseList cases={cases} onRefetch={refetch} />
              </CardContent>
            </Card>
          ) : !isLoading ? (
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
          ) : null}
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