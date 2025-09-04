'use client'

import { useState } from 'react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Textarea } from '@/components/ui/textarea'
import { Label } from '@/components/ui/label'
import { Building2, Edit, Save, X, Wand2 } from 'lucide-react'

interface Company {
  id: string
  organization_number: string
  name: string
  business_description?: string
  industry_code?: string
  website?: string
  email?: string
  phone?: string
  address?: string
  contact_person?: string
}

interface CompanyInfoProps {
  company: Company
  onUpdate: (updatedCompany: Company) => void
}

export function CompanyInfo({ company, onUpdate }: CompanyInfoProps) {
  const [isEditing, setIsEditing] = useState(false)
  const [formData, setFormData] = useState({
    name: company.name || '',
    organization_number: company.organization_number || '',
    website: company.website || '',
    email: company.email || '',
    phone: company.phone || '',
    address: company.address || '',
    contact_person: company.contact_person || '',
    business_description: company.business_description || ''
  })
  const [isSaving, setIsSaving] = useState(false)
  const [isGenerating, setIsGenerating] = useState(false)

  const handleSave = async () => {
    setIsSaving(true)
    
    try {
      const response = await fetch(`/api/v1/companies/${company.id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      })

      if (response.ok) {
        const updatedCompany = await response.json()
        onUpdate(updatedCompany)
        setIsEditing(false)
      } else {
        throw new Error('Failed to update company')
      }
    } catch (error) {
      console.error('Error updating company:', error)
      alert('Failed to update company information. Please try again.')
    } finally {
      setIsSaving(false)
    }
  }

  const handleCancel = () => {
    setFormData({
      name: company.name || '',
      organization_number: company.organization_number || '',
      website: company.website || '',
      email: company.email || '',
      phone: company.phone || '',
      address: company.address || '',
      contact_person: company.contact_person || '',
      business_description: company.business_description || ''
    })
    setIsEditing(false)
  }

  const handleChange = (field: string, value: string) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
  }

  const handleGenerateDescription = async () => {
    if (!formData.name) {
      alert('Company name is required to generate description')
      return
    }

    setIsGenerating(true)
    
    try {
      const response = await fetch(`/api/v1/companies/${company.id}/generate-description`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })

      if (response.ok) {
        const result = await response.json()
        // Update form data with generated description
        setFormData(prev => ({
          ...prev,
          business_description: result.generated_description
        }))
        // Update parent component with new company data
        onUpdate(result.company)
      } else {
        throw new Error('Failed to generate description')
      }
    } catch (error) {
      console.error('Error generating description:', error)
      alert('Failed to generate company description. Please try again.')
    } finally {
      setIsGenerating(false)
    }
  }

  return (
    <Card className="mb-6">
      <CardHeader>
        <div className="flex justify-between items-start">
          <div className="flex items-center gap-2">
            <Building2 className="w-5 h-5" />
            <CardTitle>Company Information</CardTitle>
          </div>
          <div className="flex gap-2">
            {!isEditing ? (
              <Button variant="outline" size="sm" onClick={() => setIsEditing(true)}>
                <Edit className="w-4 h-4 mr-2" />
                Edit
              </Button>
            ) : (
              <>
                <Button 
                  variant="outline" 
                  size="sm" 
                  onClick={handleCancel}
                  disabled={isSaving}
                >
                  <X className="w-4 h-4 mr-2" />
                  Cancel
                </Button>
                <Button 
                  size="sm" 
                  onClick={handleSave}
                  disabled={isSaving}
                >
                  <Save className="w-4 h-4 mr-2" />
                  {isSaving ? 'Saving...' : 'Save'}
                </Button>
              </>
            )}
          </div>
        </div>
        <CardDescription>
          Basic company details and contact information
        </CardDescription>
      </CardHeader>
      <CardContent className="space-y-4">
        {isEditing ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="company-name">Company Name</Label>
              <Input
                id="company-name"
                value={formData.name}
                onChange={(e) => handleChange('name', e.target.value)}
                placeholder="Company name"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="org-number">Organization Number</Label>
              <Input
                id="org-number"
                value={formData.organization_number}
                onChange={(e) => handleChange('organization_number', e.target.value)}
                placeholder="123456-7890"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="website">Website</Label>
              <Input
                id="website"
                type="url"
                value={formData.website}
                onChange={(e) => handleChange('website', e.target.value)}
                placeholder="https://www.company.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="email">Email</Label>
              <Input
                id="email"
                type="email"
                value={formData.email}
                onChange={(e) => handleChange('email', e.target.value)}
                placeholder="contact@company.com"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="phone">Phone</Label>
              <Input
                id="phone"
                type="tel"
                value={formData.phone}
                onChange={(e) => handleChange('phone', e.target.value)}
                placeholder="+46 8 123 456 78"
              />
            </div>
            <div className="space-y-2">
              <Label htmlFor="contact-person">Contact Person</Label>
              <Input
                id="contact-person"
                value={formData.contact_person}
                onChange={(e) => handleChange('contact_person', e.target.value)}
                placeholder="John Doe"
              />
            </div>
            <div className="space-y-2 md:col-span-2">
              <Label htmlFor="address">Address</Label>
              <Textarea
                id="address"
                value={formData.address}
                onChange={(e) => handleChange('address', e.target.value)}
                placeholder="Street address, City, Postal Code"
                rows={2}
              />
            </div>
            <div className="space-y-2 md:col-span-2">
              <div className="flex items-center justify-between">
                <Label htmlFor="business-description">Business Description</Label>
                <Button
                  type="button"
                  variant="outline"
                  size="sm"
                  onClick={handleGenerateDescription}
                  disabled={isGenerating || !formData.name}
                >
                  <Wand2 className="w-3 h-3 mr-1" />
                  {isGenerating ? 'Generating...' : 'Generate with AI'}
                </Button>
              </div>
              <Textarea
                id="business-description"
                value={formData.business_description}
                onChange={(e) => handleChange('business_description', e.target.value)}
                placeholder="Brief description of the business..."
                rows={3}
              />
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-900">Company Name</h3>
                <p className="text-gray-700">{company.name || 'Not specified'}</p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Organization Number</h3>
                <p className="text-gray-700">{company.organization_number || 'Not specified'}</p>
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Website</h3>
                {company.website ? (
                  <a 
                    href={company.website.startsWith('http') ? company.website : `https://${company.website}`}
                    target="_blank" 
                    rel="noopener noreferrer" 
                    className="text-blue-600 hover:text-blue-800 underline"
                  >
                    {company.website}
                  </a>
                ) : (
                  <p className="text-gray-500">Not specified</p>
                )}
              </div>
            </div>
            <div className="space-y-4">
              <div>
                <h3 className="font-medium text-gray-900">Email</h3>
                {company.email ? (
                  <a href={`mailto:${company.email}`} className="text-blue-600 hover:text-blue-800 underline">
                    {company.email}
                  </a>
                ) : (
                  <p className="text-gray-500">Not specified</p>
                )}
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Phone</h3>
                {company.phone ? (
                  <a href={`tel:${company.phone}`} className="text-blue-600 hover:text-blue-800">
                    {company.phone}
                  </a>
                ) : (
                  <p className="text-gray-500">Not specified</p>
                )}
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Contact Person</h3>
                <p className="text-gray-700">{company.contact_person || 'Not specified'}</p>
              </div>
            </div>
            {(company.address || company.business_description) && (
              <div className="md:col-span-2 space-y-4">
                {company.address && (
                  <div>
                    <h3 className="font-medium text-gray-900">Address</h3>
                    <p className="text-gray-700 whitespace-pre-line">{company.address}</p>
                  </div>
                )}
                {company.business_description && (
                  <div>
                    <h3 className="font-medium text-gray-900">Business Description</h3>
                    <p className="text-gray-700 whitespace-pre-line">{company.business_description}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        )}
      </CardContent>
    </Card>
  )
}