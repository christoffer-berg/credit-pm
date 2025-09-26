import './globals.css'
import { Providers } from './providers'

export const metadata = {
  title: 'Credit PM Generator',
  description: 'Automated credit memo generation service',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers>
          {children}
        </Providers>
      </body>
    </html>
  )
}
