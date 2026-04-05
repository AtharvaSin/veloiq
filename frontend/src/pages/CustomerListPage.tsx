import { useMemo, useState } from 'react'
import { useNavigate, useSearchParams } from 'react-router-dom'
import { Badge } from '@/components/ui/badge'
import { DataTable, type DataTableColumn } from '@/components/shared/DataTable'
import { FilterBar, type FilterSpec } from '@/components/shared/FilterBar'
import { PaginationControls } from '@/components/shared/PaginationControls'
import { LoadingState } from '@/components/shared/LoadingState'
import { ErrorState } from '@/components/shared/ErrorState'
import { useCustomersList } from '@/hooks/useCustomers'
import type { CustomerRead, CustomersListParams } from '@/lib/types'
import { ROUTES } from '@/lib/routes'

const FILTER_SPECS: FilterSpec[] = [
  {
    key: 'country',
    label: 'Country',
    type: 'select',
    options: [
      { label: 'Germany', value: 'DE' },
      { label: 'China', value: 'CN' },
      { label: 'India', value: 'IN' },
      { label: 'United Kingdom', value: 'GB' },
      { label: 'United States', value: 'US' },
    ],
  },
  {
    key: 'sales_area',
    label: 'Sales area',
    type: 'select',
    options: [
      { label: 'EMEA', value: 'EMEA' },
      { label: 'Greater China', value: 'Greater China' },
      { label: 'South Asia', value: 'South Asia' },
      { label: 'Americas', value: 'Americas' },
    ],
  },
]

export function CustomerListPage() {
  const navigate = useNavigate()
  const [searchParams, setSearchParams] = useSearchParams()
  const [page, setPage] = useState(() => {
    const p = searchParams.get('page')
    return p ? Number.parseInt(p, 10) : 1
  })

  const filters: Record<string, string> = {
    country: searchParams.get('country') ?? '',
    sales_area: searchParams.get('sales_area') ?? '',
  }

  const params: CustomersListParams = {
    page,
    limit: 25,
    sort: 'country',
    order: 'asc',
    ...(filters.country && { country: filters.country }),
    ...(filters.sales_area && { sales_area: filters.sales_area }),
  }

  const { data, isLoading, isError, refetch } = useCustomersList(params)

  // Client-side secondary sort: group by country, then by company name within each country.
  const sortedData = useMemo(() => {
    if (!data) return null
    const rows = [...data.data].sort((a, b) => {
      const countryCmp = a.country.localeCompare(b.country)
      if (countryCmp !== 0) return countryCmp
      return a.company_name.localeCompare(b.company_name)
    })
    return { ...data, data: rows }
  }, [data])

  function handleFilterChange(key: string, value: string) {
    const next = new URLSearchParams(searchParams)
    if (value) next.set(key, value)
    else next.delete(key)
    next.set('page', '1')
    setSearchParams(next)
    setPage(1)
  }

  function handleReset() {
    setSearchParams(new URLSearchParams())
    setPage(1)
  }

  function handlePageChange(nextPage: number) {
    const next = new URLSearchParams(searchParams)
    next.set('page', String(nextPage))
    setSearchParams(next)
    setPage(nextPage)
  }

  const columns: DataTableColumn<CustomerRead>[] = [
    {
      key: 'customer_number',
      label: 'Customer #',
      className: 'font-mono text-xs text-accent',
    },
    {
      key: 'company_name',
      label: 'Company',
      className: 'font-medium text-primary',
    },
    {
      key: 'country',
      label: 'Country',
      render: (row) => <Badge variant="outline">{row.country}</Badge>,
    },
    {
      key: 'sales_area',
      label: 'Sales area',
      className: 'text-secondary',
    },
    {
      key: 'language',
      label: 'Lang',
      className: 'font-mono text-xs text-muted',
    },
    {
      key: 'contact_name',
      label: 'Contact',
      className: 'text-secondary',
      render: (row) => row.contact_name ?? '—',
    },
  ]

  return (
    <div className="space-y-6">
      <div>
        <p className="section-label">Customer directory</p>
        <div className="flex items-center gap-3 mt-1">
          <h1 className="text-2xl font-bold text-primary">Customers</h1>
          {data && (
            <span className="inline-flex items-center rounded-tight bg-accent/10 px-2 py-0.5 font-mono text-xs font-semibold text-accent">
              {data.pagination.total} records
            </span>
          )}
        </div>
      </div>

      <FilterBar
        filters={FILTER_SPECS}
        values={filters}
        onChange={handleFilterChange}
        onReset={handleReset}
      />

      {isLoading && <LoadingState rows={8} />}
      {isError && (
        <ErrorState
          message="Failed to load customers"
          onRetry={() => refetch()}
        />
      )}
      {sortedData && (
        <>
          <DataTable
            columns={columns}
            data={sortedData.data}
            rowKey={(row) => row.id}
            onRowClick={(row) => navigate(ROUTES.CUSTOMER(row.id))}
            emptyMessage="No customers match the current filters."
          />
          <PaginationControls
            pagination={sortedData.pagination}
            onPageChange={handlePageChange}
          />
        </>
      )}
    </div>
  )
}
