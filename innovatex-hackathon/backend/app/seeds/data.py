"""Seed data — canonical questionnaire from Cuestionario_Diagnostico_Privacidad.md.

3 blocks + 11 questions. Weights sum to 100% across P2-P10.
P1 = gate (No → Bloque 1 = 0%). P11 = validation (weight 0, audit-only).
"""
import uuid as _uuid

BLOCKS = [
    {
        "slug": "politica",
        "title": "Política de Datos Personales",
        "description": "Verifica la existencia, accesibilidad, calidad y el contenido mínimo legal de la política de tratamiento de datos personales.",
        "weight": 40,
        "order_num": 1,
    },
    {
        "slug": "diseno",
        "title": "Privacidad desde el Diseño",
        "description": "Evalúa si la empresa incorpora de forma proactiva y por defecto principios y técnicas de ingeniería de privacidad desde las etapas tempranas de sus proyectos y sistemas.",
        "weight": 36,
        "order_num": 2,
    },
    {
        "slug": "gobernanza",
        "title": "Gobernanza",
        "description": "Evalúa la estructura organizacional, la asignación de responsabilidades internas y la gestión proactiva de riesgos para garantizar la protección de los datos.",
        "weight": 24,
        "order_num": 3,
    },
]

QUESTIONS = [
    # ── Bloque 1: Política (40%) ──────────────────────────────────────
    {
        "slug": "P1",
        "block_id": "politica",
        "kind": "gate",
        "text": "¿Cuenta con una política de tratamiento de datos personales?",
        "weight": 0,
        "order_num": 1,
        "gate_for": ["P2", "P3", "P4", "P5"],
    },
    {
        "slug": "P2",
        "block_id": "politica",
        "kind": "scale",
        "text": "¿La política está documentada y publicada en un medio de fácil acceso?",
        "weight": 10,
        "order_num": 2,
        "gate_for": None,
    },
    {
        "slug": "P3",
        "block_id": "politica",
        "kind": "scale",
        "text": "¿Define las finalidades del tratamiento de datos?",
        "weight": 10,
        "order_num": 3,
        "gate_for": None,
    },
    {
        "slug": "P4",
        "block_id": "politica",
        "kind": "scale",
        "text": "¿Incluye los derechos de los titulares?",
        "weight": 10,
        "order_num": 4,
        "gate_for": None,
    },
    {
        "slug": "P5",
        "block_id": "politica",
        "kind": "scale",
        "text": "¿Menciona cómo ejercer los derechos de los titulares?",
        "weight": 10,
        "order_num": 5,
        "gate_for": None,
    },
    # ── Bloque 2: Privacidad desde el Diseño (36%) ─────────────────────
    {
        "slug": "P6",
        "block_id": "diseno",
        "kind": "scale",
        "text": "¿Incorpora evaluaciones de impacto (Privacy Impact Assessments - PIA)?",
        "weight": 12,
        "order_num": 6,
        "gate_for": None,
    },
    {
        "slug": "P7",
        "block_id": "diseno",
        "kind": "scale",
        "text": "¿Aplica técnicas de minimización de datos?",
        "weight": 12,
        "order_num": 7,
        "gate_for": None,
    },
    {
        "slug": "P8",
        "block_id": "diseno",
        "kind": "scale",
        "text": "¿Configura sus sistemas para recopilar el mínimo de datos por defecto (Privacy by Default)?",
        "weight": 12,
        "order_num": 8,
        "gate_for": None,
    },
    # ── Bloque 3: Gobernanza (24%) ─────────────────────────────────────
    {
        "slug": "P9",
        "block_id": "gobernanza",
        "kind": "scale",
        "text": "¿Cuenta con un sistema de administración de riesgos asociados al tratamiento de datos personales?",
        "weight": 16,
        "order_num": 9,
        "gate_for": None,
    },
    {
        "slug": "P10",
        "block_id": "gobernanza",
        "kind": "scale",
        "text": "¿Cuenta con un Oficial de Protección de Datos Personales (DPO / Data Protection Officer)?",
        "weight": 8,
        "order_num": 10,
        "gate_for": None,
    },
    {
        "slug": "P11",
        "block_id": "gobernanza",
        "kind": "validation",
        "text": "¿Está designado formalmente el Oficial de Protección de Datos?",
        "weight": 0,
        "order_num": 11,
        "gate_for": None,
    },
]
