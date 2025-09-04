import { createServerClient, createServiceClient } from '@/lib/supabase-server'
import { NextApiRequest, NextApiResponse } from 'next'

export default async function handler(req: NextApiRequest, res: NextApiResponse) {
  if (req.method === 'GET') {
    try {
      const serviceClient = createServiceClient()
      
      const { data: cases, error } = await serviceClient
        .from('pm_cases')
        .select(`
          *,
          company:companies(*)
        `)
        .order('created_at', { ascending: false })
      
      if (error) {
        console.error('Supabase error:', error)
        return res.status(500).json({ error: 'Failed to fetch cases' })
      }
      
      return res.json(cases)
    } catch (error) {
      console.error('API error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  } else if (req.method === 'POST') {
    try {
      // Use service client for database operations (bypasses RLS)
      const serviceClient = createServiceClient()
      // Use regular client for authentication
      const supabase = createServerClient(req, res)
      
      const { organization_number, title } = req.body
      
      console.log('Creating PM case with:', { organization_number, title })
      
      // Get current user for authentication
      const { data: { user }, error: authError } = await supabase.auth.getUser()
      
      // For development, create a default user if none exists
      let currentUser = user
      if (authError || !user) {
        console.log('No authenticated user found, using development user')
        
        // Try to get existing user by email first
        const { data: existingUsers, error: getUserError } = await serviceClient.auth.admin.listUsers({
          perPage: 1,
          page: 1,
        })
        
        if (getUserError) {
          console.error('Failed to list users:', getUserError)
          return res.status(500).json({ error: 'Failed to access user system' })
        }
        
        // Find or create dev user
        let devUser = existingUsers.users.find(u => u.email === 'dev@example.com')
        
        if (!devUser) {
          // Create a user directly in the auth.users table using the service key (admin privileges)
          const { data: tempUser, error: tempUserError } = await serviceClient.auth.admin.createUser({
            email: 'dev@example.com',
            password: 'temp123',
            email_confirm: true
          })

          if (tempUserError) {
            console.error('Failed to create temp user:', tempUserError)
            return res.status(500).json({ error: 'Failed to create development user' })
          }
          devUser = tempUser.user
          console.log('Created new temporary user:', devUser.id)
        } else {
          console.log('Using existing temporary user:', devUser.id)
        }

        currentUser = devUser
        
        // Ensure user record exists in our users table
        const { error: userTableError } = await serviceClient
          .from('users')
          .upsert({
            id: currentUser.id,
            email: currentUser.email!,
            full_name: 'Development User',
            updated_at: new Date().toISOString()
          })

        if (userTableError) {
          console.error('Failed to create user in users table:', userTableError)
        }
      }

      // First, find or create the company using service client
      let { data: company, error: companyError } = await serviceClient
        .from('companies')
        .select('*')
        .eq('organization_number', organization_number)
        .single()
      
      if (companyError && companyError.code !== 'PGRST116') {
        console.error('Company fetch error:', companyError)
        return res.status(500).json({ error: 'Failed to fetch company' })
      }
      
      // If company doesn't exist, create it
      if (!company) {
        const { data: newCompany, error: createCompanyError } = await serviceClient
          .from('companies')
          .insert({
            organization_number,
            name: `Company ${organization_number}`, // Placeholder name
          })
          .select()
          .single()
        
        if (createCompanyError) {
          console.error('Company creation error:', createCompanyError)
          return res.status(500).json({ error: 'Failed to create company' })
        }
        
        company = newCompany
      }

      // Ensure user exists in our users table using service client
      if (user) {
        const { error: userUpsertError } = await serviceClient
          .from('users')
          .upsert({
            id: user.id,
            email: user.email!,
            full_name: user.user_metadata?.full_name || user.email!,
            updated_at: new Date().toISOString()
          })

        if (userUpsertError) {
          console.error('User upsert error:', userUpsertError)
        }
      }
      
      // Create the PM case using service client
      const { data: pmCase, error: caseError } = await serviceClient
        .from('pm_cases')
        .insert({
          company_id: company.id,
          title: title || `Credit Memo - ${company.name}`,
          created_by: currentUser.id,
        })
        .select(`
          *,
          company:companies(*)
        `)
        .single()
      
      if (caseError) {
        console.error('PM case creation error:', caseError)
        return res.status(500).json({ error: 'Failed to create PM case', details: caseError.message })
      }
      
      return res.json(pmCase)
    } catch (error) {
      console.error('API error:', error)
      return res.status(500).json({ error: 'Internal server error' })
    }
  } else {
    res.setHeader('Allow', ['GET', 'POST'])
    return res.status(405).json({ error: 'Method not allowed' })
  }
}