/** @type {import('next').NextConfig} */
const nextConfig = {
  env: {
    NEXT_PUBLIC_SUPABASE_URL: process.env.NEXT_PUBLIC_SUPABASE_URL,
    NEXT_PUBLIC_SUPABASE_ANON_KEY: process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY,
  },
  async rewrites() {
    return [
      {
        source: '/api/v1/:path*',
        destination: 'http://host.docker.internal:8001/api/v1/:path*',
      },
    ]
  },
}

module.exports = nextConfig