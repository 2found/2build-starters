import type { Metadata } from 'next'
import { Providers } from '@/modules/app/providers'
import './globals.css'

export const metadata: Metadata = {
  title: '__PROJECT_NAME__',
  description: '__PROJECT_NAME__ web app',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en" className="h-full antialiased">
      <body className="flex min-h-full flex-col">
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
