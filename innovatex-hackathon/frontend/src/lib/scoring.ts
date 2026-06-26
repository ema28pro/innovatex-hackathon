import type { AnswerEntry, AssessmentResult, BlockScore, BlockId, MaturityMeta } from '@/types'
import { BLOCKS, QUESTIONS } from '@/data/questionnaire'

const round2 = (n: number) => Math.round(n * 100) / 100

export function getMaturity(pct: number): MaturityMeta {
  if (pct < 40) return {
    level: 'critico', label: 'Nivel Crítico (Riesgo Alto)', color: 'red',
    description: 'La organización carece de una estructura mínima de protección de datos. Existe un alto riesgo de sanciones legales, multas y brechas de seguridad catastróficas. Se requiere intervención inmediata de la alta dirección.',
  }
  if (pct < 70) return {
    level: 'basico', label: 'Nivel Básico (Cumplimiento Reactivo)', color: 'amber',
    description: 'Se cuenta con políticas elementales escritas, pero la operación diaria no aplica los principios de privacidad de forma sistemática. La protección se ejecuta de manera reactiva ante incidentes.',
  }
  if (pct < 90) return {
    level: 'avanzado', label: 'Nivel Avanzado (Cumplimiento Proactivo)', color: 'green',
    description: 'Existe una gobernanza clara y las políticas están integradas en la mayoría de los procesos tecnológicos y organizacionales. Se gestionan los riesgos de manera estructurada con margen menor de optimización.',
  }
  return {
    level: 'optimizado', label: 'Nivel Optimizado (Liderazgo en Privacidad)', color: 'blue',
    description: 'La cultura de protección de datos personales está completamente embebida en el ADN de la organización. Las prácticas de minimización, privacidad por defecto y auditorías recurrentes garantizan resiliencia y ventaja competitiva.',
  }
}

export function computeResult(answers: Record<string, AnswerEntry>): AssessmentResult {
  let totalObtained = 0
  let maxPossible = 0
  const blocks: Record<BlockId, BlockScore> = {
    politica:   { blockId: 'politica',   obtained: 0, max: 0, pct: 0 },
    diseno:     { blockId: 'diseno',     obtained: 0, max: 0, pct: 0 },
    gobernanza: { blockId: 'gobernanza', obtained: 0, max: 0, pct: 0 },
  }

  for (const q of QUESTIONS) {
    if (q.kind !== 'scale') continue  // gate & validation carry 0 weight
    maxPossible += q.weight
    blocks[q.blockId].max += q.weight
    const a = answers[q.id]
    if (a?.scale != null) {
      const pts = (a.scale / 100) * q.weight
      totalObtained += pts
      blocks[q.blockId].obtained += pts
    }
  }

  for (const b of Object.values(blocks)) {
    b.pct = b.max > 0 ? round2((b.obtained / b.max) * 100) : 0
  }

  const totalPct = round2((totalObtained / maxPossible) * 100)
  return {
    totalPct,
    totalObtained: round2(totalObtained),
    maxPossible,
    maturity: getMaturity(totalPct),
    blocks: Object.values(blocks),
    computedAt: new Date().toISOString(),
  }
}

// Avoid unused-import errors for BLOCKS (kept for potential block-level metadata lookups)
void BLOCKS