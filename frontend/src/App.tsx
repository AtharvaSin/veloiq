import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card'
import { Separator } from '@/components/ui/separator'

function App() {
  return (
    <div className="min-h-screen bg-obsidian text-primary p-16">
      <div className="max-w-5xl mx-auto space-y-8">
        <div>
          <p className="section-label">00 — shadcn/ui Smoke Test</p>
          <h1 className="mt-2 text-4xl font-bold">VeloIQ</h1>
          <p className="mt-2 text-secondary">TÜV Rheinland Standards Automation Platform</p>
        </div>

        <Card>
          <CardHeader>
            <CardTitle>shadcn/ui primitives</CardTitle>
            <CardDescription>Mapped to DESIGN.md obsidian-aurora palette via CSS variables</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div>
              <p className="section-label mb-2">Buttons</p>
              <div className="flex flex-wrap gap-2">
                <Button variant="default">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="destructive">Destructive</Button>
                <Button variant="link">Link</Button>
              </div>
            </div>

            <Separator />

            <div>
              <p className="section-label mb-2">Badges (shadcn) + Confidence pills (custom)</p>
              <div className="flex flex-wrap gap-2">
                <Badge variant="default">Active</Badge>
                <Badge variant="secondary">Pending</Badge>
                <Badge variant="outline">Draft</Badge>
                <Badge variant="destructive">Breached</Badge>
                <span className="pill text-accent bg-accent/10">0.984 · AUTO MATCH</span>
                <span className="pill text-warn bg-warn/10">0.840 · EXPERT REVIEW</span>
                <span className="pill text-danger bg-danger/10">0.620 · MANUAL TRIAGE</span>
              </div>
            </div>

            <Separator />

            <div>
              <p className="section-label mb-2">Data typography</p>
              <p className="font-mono text-secondary">TC-44210 · 0.840 · 2026-04-06T14:32:18Z</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}

export default App
