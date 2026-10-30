import Link from 'next/link'
import { Card } from '@/modules/shared/ui/card'

export default function NotFound() {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center p-6">
      <Card>
        <h1 className="text-xl font-semibold">Page not found</h1>
        <p className="mt-2 text-muted">The page you asked for does not exist.</p>
        <Link className="mt-4 inline-block text-accent underline" href="/">Back home</Link>
      </Card>
    </main>
  )
}
