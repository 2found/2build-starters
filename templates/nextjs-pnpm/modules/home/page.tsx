import { Card } from '@/modules/shared/ui/card'

// Server component: renders the same bytes for every viewer. Viewer-specific
// state belongs in a client island (see docs/ARCHITECT-WEB.md).
export default function HomePage() {
  return (
    <main className="mx-auto flex w-full max-w-2xl flex-1 flex-col justify-center gap-4 p-6">
      <h1 className="text-3xl font-semibold">__PROJECT_NAME__</h1>
      <Card>
        <p className="text-muted">
          Edit <code className="font-mono text-ink">modules/home/page.tsx</code>. Read AGENTS.md
          before changing structure and DESIGN.md before changing visuals.
        </p>
      </Card>
    </main>
  )
}
