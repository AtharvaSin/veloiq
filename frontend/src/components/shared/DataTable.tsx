import { ChevronDown, ChevronUp, ChevronsUpDown } from 'lucide-react'
import { cn } from '@/lib/utils'
import { EmptyState } from './EmptyState'

export interface DataTableColumn<T> {
  key: keyof T | string
  label: string
  sortable?: boolean
  className?: string
  render?: (row: T) => React.ReactNode
}

export interface DataTableProps<T> {
  columns: DataTableColumn<T>[]
  data: T[]
  sortKey?: string
  sortOrder?: 'asc' | 'desc'
  onSort?: (key: string) => void
  onRowClick?: (row: T) => void
  rowKey?: (row: T) => string
  emptyMessage?: string
  className?: string
}

function resolveValue<T>(row: T, key: string): unknown {
  return (row as Record<string, unknown>)[key]
}

export function DataTable<T>({
  columns,
  data,
  sortKey,
  sortOrder,
  onSort,
  onRowClick,
  rowKey,
  emptyMessage = 'No records to display.',
  className,
}: DataTableProps<T>) {
  if (data.length === 0) {
    return <EmptyState message={emptyMessage} />
  }

  return (
    <div className={cn('overflow-x-auto rounded border border-divider', className)}>
      <table className="w-full text-sm">
        <thead className="bg-elevated">
          <tr>
            {columns.map((col) => {
              const isActive = sortKey === col.key
              return (
                <th
                  key={String(col.key)}
                  className={cn(
                    'px-4 py-3 text-left uppercase tracking-label text-xs font-semibold text-accent',
                    col.sortable && 'cursor-pointer select-none hover:bg-elevated/70',
                    col.className,
                  )}
                  onClick={
                    col.sortable && onSort ? () => onSort(String(col.key)) : undefined
                  }
                >
                  <span className="inline-flex items-center gap-1">
                    {col.label}
                    {col.sortable && (
                      isActive ? (
                        sortOrder === 'asc' ? (
                          <ChevronUp className="h-3 w-3" />
                        ) : (
                          <ChevronDown className="h-3 w-3" />
                        )
                      ) : (
                        <ChevronsUpDown className="h-3 w-3 text-muted" />
                      )
                    )}
                  </span>
                </th>
              )
            })}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr
              key={rowKey ? rowKey(row) : idx}
              className={cn(
                'border-t border-divider transition-colors',
                idx % 2 === 0 ? 'bg-surface' : 'bg-obsidian',
                onRowClick && 'cursor-pointer hover:bg-elevated hover:border-l-2 hover:border-l-accent',
              )}
              onClick={onRowClick ? () => onRowClick(row) : undefined}
            >
              {columns.map((col) => (
                <td
                  key={String(col.key)}
                  className={cn('px-4 py-3 text-secondary', col.className)}
                >
                  {col.render
                    ? col.render(row)
                    : String(resolveValue(row, String(col.key)) ?? '—')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
