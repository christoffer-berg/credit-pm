import { createPagesServerClient } from '@supabase/auth-helpers-nextjs'
import { createClient } from '@supabase/supabase-js'
import { NextApiRequest, NextApiResponse } from 'next'

export const createServerClient = (req?: NextApiRequest, res?: NextApiResponse) => {
  if (req && res) {
    return createPagesServerClient({ req, res })
  }
  // Fallback for cases where req/res aren't available
  return createClient(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!
  )
}

export const createServiceClient = () => {
  const supabaseUrl = process.env.SUPABASE_URL!
  const supabaseServiceKey = process.env.SUPABASE_SERVICE_KEY!
  
  return createClient(supabaseUrl, supabaseServiceKey, {
    auth: {
      autoRefreshToken: false,
      persistSession: false
    }
  })
}