/**
 * TypeScript mirrors of backend Pydantic schemas.
 * Keep field names and types IDENTICAL to the backend schemas.
 * Source of truth: backend/app/schemas/*.py
 */

// ============ Primitive aliases ============
export type UUID = string
export type ISODateTime = string
export type ISODate = string
export type DecimalStr = string // Pydantic Decimal serialized as string

// ============ Enums (mirror CHECK constraints) ============
export type CertificateStatus = 'active' | 'expiring' | 'expired' | 'suspended'
export type ConfidenceTier = 'auto_match' | 'expert_review' | 'manual_triage'
export type MatchStatus = 'pending' | 'reviewed'
export type ImpactClassification =
  | 'no_change'
  | 'administrative'
  | 'minor_technical'
  | 'major_technical'
  | 'safety_critical'
export type ActionRequired = 'reconfirm' | 'retest' | 'suspend' | 'withdraw'
export type Decision = 'approved' | 'rejected' | 'escalated'
export type NotificationStatus =
  | 'queued'
  | 'sent'
  | 'delivered'
  | 'opened'
  | 'clicked'
  | 'bounced'
  | 'breached'
export type EscalationStatus = 'open' | 'contacted' | 'resolved'

// ============ Pagination + errors ============
export interface PaginationMeta {
  page: number
  limit: number
  total: number
  total_pages: number
}

export interface PaginatedResponse<T> {
  data: T[]
  pagination: PaginationMeta
}

export interface ErrorResponse {
  error: string
  code: string
  entity?: string | null
  id?: string | null
  rule?: string | null
}

export interface ValidationErrorResponse {
  error: string
  code: string
  fields: Record<string, string>
}

// ============ Customer ============
export interface CustomerBase {
  customer_number: string
  company_name: string
  country: string
  sales_area: string
  language: string
  contact_name?: string | null
  contact_email?: string | null
}

export interface CustomerCreate extends CustomerBase {}

export interface CustomerUpdate {
  company_name?: string | null
  country?: string | null
  sales_area?: string | null
  language?: string | null
  contact_name?: string | null
  contact_email?: string | null
}

export interface CustomerRead extends CustomerBase {
  id: UUID
  created_at: ISODateTime
}

// ============ Standard ============
export interface StandardBase {
  ac_code: string
  title: string
  status: string
  replaced_by?: string | null
  committee?: string | null
  ics_code?: string | null
}

export interface StandardCreate extends StandardBase {
  source_payload: Record<string, unknown>
}

export interface StandardUpdate {
  title?: string | null
  status?: string | null
  replaced_by?: string | null
  committee?: string | null
  ics_code?: string | null
}

export interface StandardRead extends StandardBase {
  id: UUID
  normalized_code: string
  base_number: string
  version_year?: number | null
  ingested_at: ISODateTime
  created_at: ISODateTime
  updated_at: ISODateTime
}

// ============ Certificate ============
export interface CertificateBase {
  certificate_number: string
  customer_id: UUID
  product_description: string
  status: CertificateStatus
  issue_date: ISODate
  expiry_date: ISODate
}

export interface CertificateCreate extends CertificateBase {}

export interface CertificateUpdate {
  product_description?: string | null
  status?: CertificateStatus | null
  issue_date?: ISODate | null
  expiry_date?: ISODate | null
}

export interface CertificateRead extends CertificateBase {
  id: UUID
  created_at: ISODateTime
  updated_at: ISODateTime
}

// ============ CertStandardLink ============
export interface CertStandardLinkBase {
  standard_ref: string
  normalized_ref: string
  base_number: string
}

export interface CertStandardLinkCreate extends CertStandardLinkBase {
  certificate_id: UUID
}

export interface CertStandardLinkUpdate {
  standard_ref?: string | null
  normalized_ref?: string | null
  base_number?: string | null
}

export interface CertStandardLinkRead extends CertStandardLinkBase {
  id: UUID
  certificate_id: UUID
  linked_at: ISODateTime
}

// ============ MatchResult (read-only in Phase A) ============
export interface MatchResultRead {
  id: UUID
  natos_standard_id: UUID
  cert_link_id: UUID
  similarity_score: DecimalStr
  levenshtein_score?: DecimalStr | null
  jaro_winkler_score?: DecimalStr | null
  token_set_score?: DecimalStr | null
  confidence_tier: ConfidenceTier
  status: MatchStatus
  matched_at: ISODateTime
  reviewed_at?: ISODateTime | null
}

// ============ Assessment (read-only in Phase A) ============
export interface AssessmentRead {
  id: UUID
  match_result_id: UUID
  assessor_id: string
  impact_classification: ImpactClassification
  action_required: ActionRequired
  reason_code: string
  notes?: string | null
  decision: Decision
  decided_at: ISODateTime
  signature_hash: string
}

// ============ Notification (read-only in Phase A) ============
export interface NotificationRead {
  id: UUID
  assessment_id: UUID
  customer_id: UUID
  template_language: string
  subject: string
  body_html: string
  status: NotificationStatus
  sent_at?: ISODateTime | null
  delivered_at?: ISODateTime | null
  opened_at?: ISODateTime | null
  clicked_at?: ISODateTime | null
  sla_deadline: ISODateTime
}

// ============ SalesEscalation ============
export interface SalesEscalationRead {
  id: UUID
  notification_id: UUID
  customer_id: UUID
  escalation_reason: string
  opportunity_value: DecimalStr
  assigned_to?: string | null
  status: EscalationStatus
  created_at: ISODateTime
  resolved_at?: ISODateTime | null
}

export interface SalesEscalationUpdate {
  status?: EscalationStatus | null
  assigned_to?: string | null
}

// ============ AuditLog (read-only) ============
export interface AuditLogRead {
  id: UUID
  entity_type: string
  entity_id: UUID
  action: string
  actor: string
  details: Record<string, unknown>
  ip_address?: string | null
  created_at: ISODateTime
}

// ============ List query parameter types (mirrors router Query params) ============
export interface ListParams {
  page?: number
  limit?: number
  sort?: string
  order?: 'asc' | 'desc'
}

export interface StandardsListParams extends ListParams {
  status?: string
  committee?: string
  base_number?: string
}

export interface CustomersListParams extends ListParams {
  country?: string
  sales_area?: string
}

export interface CertificatesListParams extends ListParams {
  customer_id?: UUID
  status?: CertificateStatus
}

export interface MatchesListParams extends ListParams {
  confidence_tier?: ConfidenceTier
  status?: MatchStatus
  natos_standard_id?: UUID
}

export interface AssessmentsListParams extends ListParams {
  assessor_id?: string
  decision?: Decision
  impact_classification?: ImpactClassification
  match_result_id?: UUID
}

export interface NotificationsListParams extends ListParams {
  customer_id?: UUID
  status?: NotificationStatus
}

export interface EscalationsListParams extends ListParams {
  status?: EscalationStatus
  customer_id?: UUID
  assigned_to?: string
}

export interface AuditListParams extends ListParams {
  entity_type?: string
  entity_id?: UUID
  actor?: string
  action?: string
  from?: ISODateTime
  to?: ISODateTime
}
