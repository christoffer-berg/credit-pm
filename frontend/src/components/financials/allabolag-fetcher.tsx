'use client'

import { useState } from 'react'
// import { useSupabaseClient } from '@supabase/auth-helpers-react'
import { apiClient } from '@/lib/api-client'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card'
import { Badge } from '@/components/ui/badge'
import { Alert, AlertDescription } from '@/components/ui/alert'
import { Globe, Search, CheckCircle, AlertCircle, Info } from 'lucide-react'

interface AllabolagFetcherProps {
  companyId: string
  companyName: string
  orgNumber?: string
  onSuccess?: () => void
}

interface FetchResult {
  success: boolean
  data?: {
    company_info: {
      name: string
      org_number: string
      industry: string
    }
    statements_found: number
    years_extracted: number[]
    latest_year: number
  }
  error?: string
}

export function AllabolagFetcher({ companyId, companyName, orgNumber, onSuccess }: AllabolagFetcherProps) {
  const [searchQuery, setSearchQuery] = useState(orgNumber || companyName)
  const [isLoading, setIsLoading] = useState(false)
  const [result, setResult] = useState<FetchResult | null>(null)
  // const supabase = useSupabaseClient()

  const handleFetch = async () => {
    if (!searchQuery.trim()) return

    setIsLoading(true)
    setResult(null)

    try {
      const data = (await apiClient.fetchAllabolag(companyId, {
        query: searchQuery.trim(),
        ...(orgNumber ? { org_number: orgNumber } : {}),
      })) as FetchResult['data']

      if (data) {
        setResult({ success: true, data })
        onSuccess?.()
      } else {
        setResult({ 
          success: false, 
          error: 'Failed to fetch data from Allabolag.se' 
        })
      }
    } catch (error) {
      setResult({ 
        success: false, 
        error: error instanceof Error ? error.message : 'Network error occurred' 
      })
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleFetch()
    }
  }

  return (
    <div className="space-y-4">
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-lg">
            <Globe className="h-5 w-5 text-blue-500" />
            Fetch from Allabolag.se
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex space-x-2">
            <Input
              placeholder="Enter company name or organization number"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <Button
              onClick={handleFetch}
              disabled={isLoading || !searchQuery.trim()}
              className="min-w-[100px]"
            >
              <Search className="h-4 w-4 mr-2" />
              {isLoading ? 'Searching...' : 'Fetch'}
            </Button>
          </div>

          <Alert>
            <Info className="h-4 w-4" />
            <AlertDescription>
              This will automatically fetch financial statements from allabolag.se. 
              Use the organization number (e.g. "556016-0680") for best results.
            </AlertDescription>
          </Alert>

          {/* Results */}
          {result && (
            <Card>
              <CardContent className="pt-4">
                {result.success ? (
                  <div className="space-y-3">
                    <div className="flex items-center gap-2">
                      <CheckCircle className="h-5 w-5 text-green-500" />
                      <span className="font-medium text-green-700">Successfully fetched data!</span>
                    </div>
                    
                    {result.data && (
                      <div className="space-y-3">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                          <div>
                            <span className="font-medium">Company:</span> {result.data.company_info.name}
                          </div>
                          <div>
                            <span className="font-medium">Org Number:</span> {result.data.company_info.org_number}
                          </div>
                          <div>
                            <span className="font-medium">Industry:</span> {result.data.company_info.industry}
                          </div>
                          <div>
                            <span className="font-medium">Latest Year:</span> {result.data.latest_year}
                          </div>
                        </div>

                        <div className="flex items-center gap-2">
                          <Badge variant="secondary">
                            {result.data.statements_found} statements found
                          </Badge>
                          <Badge variant="outline">
                            Years: {result.data.years_extracted.join(', ')}
                          </Badge>
                        </div>

                        <div className="text-xs text-gray-500 mt-2">
                          ✓ Financial data has been imported and is ready for analysis
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-2">
                    <div className="flex items-center gap-2">
                      <AlertCircle className="h-5 w-5 text-red-500" />
                      <span className="font-medium text-red-700">Fetch failed</span>
                    </div>
                    <p className="text-sm text-red-600">{result.error}</p>
                    <div className="text-xs text-gray-500 mt-2">
                      Try using the exact organization number or check if the company exists on allabolag.se
                    </div>
                  </div>
                )}
              </CardContent>
            </Card>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
