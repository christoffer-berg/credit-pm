'use client'

import { useState, useCallback } from 'react'
import { useSupabaseClient } from '@supabase/auth-helpers-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'
import { Progress } from '@/components/ui/progress'
import { Upload, File, AlertCircle, CheckCircle, X } from 'lucide-react'
import { useDropzone } from 'react-dropzone'

interface PDFUploaderProps {
  companyId: string
  onSuccess?: () => void
}

interface UploadStatus {
  file: File
  progress: number
  status: 'pending' | 'uploading' | 'processing' | 'completed' | 'error'
  error?: string
  extractedData?: any
}

export function PDFUploader({ companyId, onSuccess }: PDFUploaderProps) {
  const [uploads, setUploads] = useState<UploadStatus[]>([])
  const supabase = useSupabaseClient()

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const newUploads = acceptedFiles.map(file => ({
      file,
      progress: 0,
      status: 'pending' as const,
    }))
    setUploads(prev => [...prev, ...newUploads])

    // Start uploading each file
    newUploads.forEach((upload, index) => {
      uploadFile(upload.file, uploads.length + index)
    })
  }, [uploads.length])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'application/pdf': ['.pdf'],
    },
    maxFiles: 5,
  })

  const uploadFile = async (file: File, index: number) => {
    try {
      setUploads(prev => prev.map((upload, i) => 
        i === index ? { ...upload, status: 'uploading', progress: 0 } : upload
      ))

      const session = await supabase.auth.getSession()
      const formData = new FormData()
      formData.append('file', file)

      const xhr = new XMLHttpRequest()
      
      xhr.upload.onprogress = (event) => {
        if (event.lengthComputable) {
          const progress = Math.round((event.loaded / event.total) * 100)
          setUploads(prev => prev.map((upload, i) => 
            i === index ? { ...upload, progress } : upload
          ))
        }
      }

      xhr.onload = () => {
        if (xhr.status === 200) {
          setUploads(prev => prev.map((upload, i) => 
            i === index ? { 
              ...upload, 
              status: 'processing',
              progress: 100,
            } : upload
          ))

          // Parse the response to get extracted data
          try {
            const response = JSON.parse(xhr.responseText)
            setUploads(prev => prev.map((upload, i) => 
              i === index ? { 
                ...upload, 
                status: 'completed',
                extractedData: response
              } : upload
            ))
            onSuccess?.()
          } catch (parseError) {
            setUploads(prev => prev.map((upload, i) => 
              i === index ? { 
                ...upload, 
                status: 'error',
                error: 'Failed to parse response'
              } : upload
            ))
          }
        } else {
          setUploads(prev => prev.map((upload, i) => 
            i === index ? { 
              ...upload, 
              status: 'error',
              error: `Upload failed: ${xhr.statusText}`
            } : upload
          ))
        }
      }

      xhr.onerror = () => {
        setUploads(prev => prev.map((upload, i) => 
          i === index ? { 
            ...upload, 
            status: 'error',
            error: 'Network error during upload'
          } : upload
        ))
      }

      xhr.open('POST', `/api/v1/financials/companies/${companyId}/upload-pdf`)
      xhr.setRequestHeader('Authorization', `Bearer ${session.data.session?.access_token}`)
      xhr.send(formData)

    } catch (error) {
      setUploads(prev => prev.map((upload, i) => 
        i === index ? { 
          ...upload, 
          status: 'error',
          error: error instanceof Error ? error.message : 'Unknown error'
        } : upload
      ))
    }
  }

  const removeUpload = (index: number) => {
    setUploads(prev => prev.filter((_, i) => i !== index))
  }

  const getStatusIcon = (status: UploadStatus['status']) => {
    switch (status) {
      case 'completed':
        return <CheckCircle className="h-5 w-5 text-green-500" />
      case 'error':
        return <AlertCircle className="h-5 w-5 text-red-500" />
      case 'uploading':
      case 'processing':
        return <div className="h-5 w-5 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      default:
        return <File className="h-5 w-5 text-gray-400" />
    }
  }

  const getStatusText = (upload: UploadStatus) => {
    switch (upload.status) {
      case 'pending':
        return 'Pending...'
      case 'uploading':
        return `Uploading... ${upload.progress}%`
      case 'processing':
        return 'Processing PDF...'
      case 'completed':
        return `Extracted ${upload.extractedData?.statements_found || 0} financial statements`
      case 'error':
        return upload.error || 'Upload failed'
      default:
        return ''
    }
  }

  return (
    <div className="space-y-4">
      {/* Drop Zone */}
      <Card>
        <CardContent className="p-6">
          <div
            {...getRootProps()}
            className={`
              border-2 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors
              ${isDragActive 
                ? 'border-primary bg-primary/5' 
                : 'border-gray-300 hover:border-primary hover:bg-primary/5'
              }
            `}
          >
            <input {...getInputProps()} />
            <Upload className="h-12 w-12 mx-auto mb-4 text-gray-400" />
            {isDragActive ? (
              <p className="text-lg mb-2">Drop the PDF files here...</p>
            ) : (
              <div>
                <p className="text-lg mb-2">Drag & drop PDF files here</p>
                <p className="text-sm text-gray-500 mb-4">or click to select files</p>
                <Button variant="outline">
                  Select PDF Files
                </Button>
              </div>
            )}
            <p className="text-xs text-gray-400 mt-4">
              Upload annual reports, financial statements (PDF format only, max 5 files)
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Upload Progress */}
      {uploads.length > 0 && (
        <Card>
          <CardContent className="p-4">
            <h3 className="font-semibold mb-4">Upload Progress</h3>
            <div className="space-y-3">
              {uploads.map((upload, index) => (
                <div key={index} className="flex items-center space-x-3 p-3 bg-gray-50 rounded-lg">
                  <div className="flex-shrink-0">
                    {getStatusIcon(upload.status)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center justify-between mb-1">
                      <p className="text-sm font-medium truncate">
                        {upload.file.name}
                      </p>
                      <button
                        onClick={() => removeUpload(index)}
                        className="text-gray-400 hover:text-gray-600"
                      >
                        <X className="h-4 w-4" />
                      </button>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <p className="text-xs text-gray-500">
                        {getStatusText(upload)}
                      </p>
                      <span className="text-xs text-gray-400">
                        ({(upload.file.size / 1024 / 1024).toFixed(1)} MB)
                      </span>
                    </div>
                    
                    {(upload.status === 'uploading' || upload.status === 'processing') && (
                      <Progress value={upload.progress} className="mt-2 h-2" />
                    )}

                    {upload.status === 'completed' && upload.extractedData && (
                      <div className="mt-2 text-xs text-green-600">
                        ✓ Successfully extracted financial data for years: {
                          upload.extractedData.years_extracted?.join(', ') || 'Unknown'
                        }
                      </div>
                    )}

                    {upload.status === 'error' && (
                      <div className="mt-2 text-xs text-red-600">
                        ✗ {upload.error}
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}