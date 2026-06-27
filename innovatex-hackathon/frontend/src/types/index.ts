// ───────────────────────── Company / Onboarding ─────────────────────────
export type Sector =
  | 'tecnologia' | 'salud' | 'finanzas' | 'comercio'
  | 'manufactura' | 'educacion' | 'gobierno' | 'otro';

export type CompanySize =
  | 'micro'   // 1-10
  | 'pequena' // 11-50
  | 'mediana' // 51-200
  | 'grande'; // 200+

export interface Company {
  id: string;
  companyName: string;   // mapped from API `name`
  nit: string;
  sector: Sector;
  size: CompanySize;
  contactEmail?: string;
  createdAt: string;
}

export interface CompanyCreate {
  name: string;          // matches backend field name
  nit: string;
  sector: Sector;
  size: CompanySize;
  contact_email?: string;
}

// ───────────────────────── Assessment ─────────────────────────
export type BlockId = 'politica' | 'diseno' | 'gobernanza';

export interface Block {
  id: BlockId;
  title: string;
  description: string;
  weight: number;          // 40 | 36 | 24
}

export type AnswerScale = 0 | 35 | 70 | 100;
export type GateAnswer = 'si' | 'no';
export type ValidationAnswer = 'si' | 'no';
export type QuestionKind = 'gate' | 'scale' | 'validation';

export interface QuestionOption {
  scale: AnswerScale;
  label: string;
  description: string;
  points: number;     // (scale/100) * question.weight
}

export interface Question {
  id: string;              // "P1".."P11"
  blockId: BlockId;
  kind: QuestionKind;
  order: number;
  text: string;
  weight: number;
  gateFor?: string[];
  options: QuestionOption[];
}

export interface AnswerEntry {
  questionId: string;
  kind: QuestionKind;
  scale?: AnswerScale;
  gate?: GateAnswer;
  validation?: ValidationAnswer;
  forced?: boolean;
  notes?: string;
  updatedAt: string;
}

export type AssessmentStatus = 'draft' | 'completed';

export interface BlockScore {
  blockId: BlockId;
  obtained: number;
  max: number;
  pct: number;
}

export type MaturityLevel = 'critico' | 'basico' | 'avanzado' | 'optimizado';

export interface MaturityMeta {
  level: MaturityLevel;
  label: string;
  color: 'red' | 'amber' | 'green' | 'blue';
  description: string;
}

export interface AssessmentResult {
  totalPct: number;
  totalObtained: number;
  maxPossible: number;
  maturity: MaturityMeta;
  blocks: BlockScore[];
  computedAt: string;
}

export interface Assessment {
  id: string;
  companyId: string;
  userId: string;
  status: AssessmentStatus;
  answers: Record<string, AnswerEntry>;
  result: AssessmentResult | null;
  createdAt: string;
  completedAt: string | null;
}

// ───────────────────────── API raw answer / recommendations ─────────────────────────
export interface AssessmentAnswerRaw {
  id?: string
  assessmentId: string
  questionId: string
  kind: QuestionKind
  scaleResp?: 0 | 35 | 70 | 100
  gateResp?: boolean
  validationResp?: boolean
  notes?: string | null
  answeredAt: string
}

export interface Recommendation {
  id: string
  assessmentId: string
  blockId: BlockId
  priority: 'high' | 'medium' | 'low'
  title: string
  body: string
  createdAt: string
}

export interface ActionItem {
  id: string
  recommendationId: string
  title: string
  status: 'pending' | 'in_progress' | 'completed'
  assignedTo?: string | null
  createdAt: string
}

// ───────────────────────── Remediation Plan (Phase 7) ────────────────────────
export interface WeakQuestion {
  questionSlug: string
  questionText: string
  currentAnswer: string
  blockTitle: string
  kind: 'gate' | 'scale' | 'validation'
}

export interface RemediationPlanItem {
  questionSlug: string
  questionText: string
  currentAnswer: string
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  steps: string[]
}

export interface RemediationPlan {
  assessmentId: string
  overallScore: number | null
  maturityLevel: string
  maturityLabel: string
  weakQuestions: WeakQuestion[]
  planItems: RemediationPlanItem[]
  generatedAt: string | null
  error: string | null
}
