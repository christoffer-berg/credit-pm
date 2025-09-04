'use client'

import { useState } from 'react'
import { Button } from '@/components/ui/button'
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { CreatePMCaseRequest } from '@/types'

interface CreateCaseDialogProps {
  open: boolean
  onOpenChange: (open: boolean) => void
  onCaseCreated: () => void
}

export function CreateCaseDialog({ open, onOpenChange, onCaseCreated }: CreateCaseDialogProps) {
  const [organizationNumber, setOrganizationNumber] = useState('')
  const [title, setTitle] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')

    try {
      const response = await fetch('/api/v1/cases', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          organization_number: organizationNumber,
          title: title || undefined,
        } as CreatePMCaseRequest),
      })

      if (!response.ok) {
        const errorData = await response.json()
        console.error('API Error:', errorData)
        throw new Error(errorData.error || errorData.details || 'Failed to create case')
      }

      setOrganizationNumber('')
      setTitle('')
      onCaseCreated()
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An unexpected error occurred')
    } finally {
      setLoading(false)
    }
  }

  const formatOrganizationNumber = (value: string) => {
    const cleaned = value.replace(/\D/g, '')
    if (cleaned.length <= 6) {
      return cleaned
    }
    return cleaned.slice(0, 6) + '-' + cleaned.slice(6, 10)
  }

  const handleOrganizationNumberChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const formatted = formatOrganizationNumber(e.target.value)
    setOrganizationNumber(formatted)
  }

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      <DialogContent className="sm:max-w-md">
        <DialogHeader>
          <DialogTitle>Create New Credit PM</DialogTitle>
          <DialogDescription>
            Enter the company's organization number to get started
          </DialogDescription>
        </DialogHeader>
        <form onSubmit={handleSubmit}>
          <div className="grid gap-4 py-4">
            <div>
              <Label htmlFor="orgNumber">Organization Number</Label>
              <Input
                id="orgNumber"
                placeholder="556016-0680"
                value={organizationNumber}
                onChange={handleOrganizationNumberChange}
                maxLength={11}
                required
              />
            </div>
            <div>
              <Label htmlFor="title">Title (Optional)</Label>
              <Input
                id="title"
                placeholder="Credit PM for..."
                value={title}
                onChange={(e) => setTitle(e.target.value)}
              />
            </div>
            {error && (
              <div className="text-red-600 text-sm">{error}</div>
            )}
          </div>
          <DialogFooter>
            <Button
              type="button"
              variant="outline"
              onClick={() => onOpenChange(false)}
            >
              Cancel
            </Button>
            <Button type="submit" disabled={loading}>
              {loading ? 'Creating...' : 'Create PM'}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}