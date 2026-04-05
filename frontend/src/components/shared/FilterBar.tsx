import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'
import { Button } from '@/components/ui/button'
import { X } from 'lucide-react'
import { cn } from '@/lib/utils'

export interface FilterSpec {
  key: string
  label: string
  type: 'select' | 'text'
  options?: { label: string; value: string }[]
  placeholder?: string
  autoComplete?: string
}

interface FilterBarProps {
  filters: FilterSpec[]
  values: Record<string, string>
  onChange: (key: string, value: string) => void
  onReset?: () => void
  className?: string
}

export function FilterBar({
  filters,
  values,
  onChange,
  onReset,
  className,
}: FilterBarProps) {
  const hasActiveFilters = Object.values(values).some((v) => v && v.length > 0)

  return (
    <div
      className={cn(
        'flex flex-wrap items-end gap-3 p-4 bg-surface border border-divider rounded',
        className,
      )}
    >
      {filters.map((filter) => {
        const current = values[filter.key] ?? ''
        return (
          <div key={filter.key} className="flex flex-col gap-1.5 min-w-[160px]">
            <Label htmlFor={`filter-${filter.key}`} className="text-xs text-muted uppercase tracking-label">
              {filter.label}
            </Label>
            {filter.type === 'select' && filter.options ? (
              <Select
                value={current || undefined}
                onValueChange={(v) => onChange(filter.key, v === '__all__' ? '' : v)}
              >
                <SelectTrigger id={`filter-${filter.key}`} className="bg-obsidian">
                  <SelectValue placeholder={filter.placeholder ?? 'All'} />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="__all__">All</SelectItem>
                  {filter.options.map((opt) => (
                    <SelectItem key={opt.value} value={opt.value}>
                      {opt.label}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            ) : (
              <Input
                id={`filter-${filter.key}`}
                type="text"
                placeholder={filter.placeholder}
                value={current}
                onChange={(e) => onChange(filter.key, e.target.value)}
                autoComplete={filter.autoComplete}
                className="bg-obsidian"
              />
            )}
          </div>
        )
      })}
      {hasActiveFilters && onReset && (
        <Button variant="ghost" size="sm" onClick={onReset}>
          <X className="h-4 w-4 mr-1" />
          Clear
        </Button>
      )}
    </div>
  )
}
