import type { Block, Question } from '@/types'

export const BLOCKS: Block[] = [
  {
    id: 'politica',
    title: 'Política de Datos Personales',
    description:
      'Verifica la existencia, accesibilidad, calidad y el contenido mínimo legal de la política de tratamiento de datos personales.',
    weight: 40,
  },
  {
    id: 'diseno',
    title: 'Privacidad desde el Diseño',
    description:
      'Evalúa si la empresa incorpora de forma proactiva y por defecto principios y técnicas de ingeniería de privacidad desde las etapas tempranas de sus proyectos y sistemas.',
    weight: 36,
  },
  {
    id: 'gobernanza',
    title: 'Gobernanza',
    description:
      'Evalúa la estructura organizacional, la asignación de responsabilidades internas y la gestión proactiva de riesgos para garantizar la protección de los datos.',
    weight: 24,
  },
]

export const QUESTIONS: Question[] = [
  // P1 — Gate
  {
    id: 'P1',
    blockId: 'politica',
    kind: 'gate',
    order: 1,
    text: '¿Cuenta con una política de tratamiento de datos personales?',
    weight: 0,
    gateFor: ['P2', 'P3', 'P4', 'P5'],
    options: [],
  },
  // P2
  {
    id: 'P2',
    blockId: 'politica',
    kind: 'scale',
    order: 2,
    text: '¿La política está documentada y publicada en un medio de fácil acceso?',
    weight: 10,
    options: [
      { scale: 0, label: 'No', description: 'No está documentada ni publicada.', points: 0 },
      { scale: 35, label: 'Inicial', description: 'Está documentada en borrador interno, pero no se ha publicado ni difundido.', points: 3.5 },
      { scale: 70, label: 'Parcial', description: 'Está aprobada y publicada, pero su acceso es difícil para el titular (ej. oculta en menús secundarios) o solo se encuentra en canales físicos restringidos.', points: 7.0 },
      { scale: 100, label: 'Total', description: 'Está formalmente aprobada, actualizada y publicada en la página web principal y canales de atención de manera visible y accesible de un solo clic.', points: 10.0 },
    ],
  },
  // P3
  {
    id: 'P3',
    blockId: 'politica',
    kind: 'scale',
    order: 3,
    text: '¿Define las finalidades del tratamiento de datos?',
    weight: 10,
    options: [
      { scale: 0, label: 'No', description: 'No se mencionan las finalidades para las cuales se recolectan los datos.', points: 0 },
      { scale: 35, label: 'Inicial', description: 'Se mencionan de forma genérica y ambigua (ej. "para fines comerciales y operativos") sin especificar el alcance real.', points: 3.5 },
      { scale: 70, label: 'Parcial', description: 'Se definen las finalidades de forma detallada para algunos tipos de titulares (ej. clientes), pero se omiten otros grupos (ej. empleados, proveedores).', points: 7.0 },
      { scale: 100, label: 'Total', description: 'Se definen de manera clara, explícita, específica y lícita las finalidades del tratamiento para cada categoría de titular de datos.', points: 10.0 },
    ],
  },
  // P4
  {
    id: 'P4',
    blockId: 'politica',
    kind: 'scale',
    order: 4,
    text: '¿Incluye los derechos de los titulares?',
    weight: 10,
    options: [
      { scale: 0, label: 'No', description: 'No se mencionan los derechos de los usuarios/titulares en el documento.', points: 0 },
      { scale: 35, label: 'Inicial', description: 'Se hace una mención genérica a la ley de privacidad, pero no se listan explícitamente cuáles son los derechos.', points: 3.5 },
      { scale: 70, label: 'Parcial', description: 'Se listan los derechos básicos (Acceso, Rectificación), pero se omiten derechos modernos o locales específicos (ej. Cancelación, Oposición, Portabilidad, Supresión).', points: 7.0 },
      { scale: 100, label: 'Total', description: 'Se desglosan de forma taxativa y clara todos los derechos aplicables que le asisten al titular bajo la normatividad vigente.', points: 10.0 },
    ],
  },
  // P5
  {
    id: 'P5',
    blockId: 'politica',
    kind: 'scale',
    order: 5,
    text: '¿Menciona cómo ejercer los derechos de los titulares?',
    weight: 10,
    options: [
      { scale: 0, label: 'No', description: 'No establece canales ni procedimientos para que los usuarios radiquen consultas o reclamos.', points: 0 },
      { scale: 35, label: 'Inicial', description: 'Menciona que se pueden ejercer los derechos, pero no provee ningún canal de contacto (correo, teléfono o dirección).', points: 3.5 },
      { scale: 70, label: 'Parcial', description: 'Indica un canal de contacto (ej. un correo electrónico institucional genérico), pero no define el procedimiento interno, los requisitos del mensaje ni los tiempos de respuesta.', points: 7.0 },
      { scale: 100, label: 'Total', description: 'Define canales específicos y gratuitos (correo exclusivo, formularios), junto con un procedimiento claro, los requisitos de la solicitud y los tiempos de respuesta estipulados por ley.', points: 10.0 },
    ],
  },
  // P6
  {
    id: 'P6',
    blockId: 'diseno',
    kind: 'scale',
    order: 6,
    text: '¿Incorpora evaluaciones de impacto (Privacy Impact Assessments - PIA)?',
    weight: 12,
    options: [
      { scale: 0, label: 'No', description: 'No se realizan evaluaciones de impacto bajo ningún escenario.', points: 0 },
      { scale: 35, label: 'Inicial', description: 'Se analizan los riesgos de privacidad de manera informal en reuniones, pero no hay metodologías ni registros documentados.', points: 4.2 },
      { scale: 70, label: 'Parcial', description: 'Se ejecutan metodologías de evaluación de impacto de manera reactiva, únicamente cuando ocurre un incidente o ante un requerimiento legal estricto.', points: 8.4 },
      { scale: 100, label: 'Total', description: 'Se cuenta con una política y plantilla formal de PIA que se aplica obligatoriamente a todo nuevo producto, servicio, software o tratamiento de datos de alto riesgo antes de su implementación.', points: 12.0 },
    ],
  },
  // P7
  {
    id: 'P7',
    blockId: 'diseno',
    kind: 'scale',
    order: 7,
    text: '¿Aplica técnicas de minimización de datos?',
    weight: 12,
    options: [
      { scale: 0, label: 'No', description: 'Se recolectan y almacenan todos los datos posibles bajo la premisa de "por si se necesitan en el futuro".', points: 0 },
      { scale: 35, label: 'Inicial', description: 'Existe la directriz teórica de no pedir datos innecesarios, pero no se ha revisado si los formularios actuales la cumplen.', points: 4.2 },
      { scale: 70, label: 'Parcial', description: 'Se han depurado algunos formularios o bases de datos reduciendo campos innecesarios, pero no es una práctica estandarizada en el desarrollo técnico.', points: 8.4 },
      { scale: 100, label: 'Total', description: 'Cada base de datos, API y formulario de recolección pasa por un proceso de validación técnica donde se demuestra la estricta necesidad e idoneidad de cada dato solicitado respecto a la finalidad.', points: 12.0 },
    ],
  },
  // P8
  {
    id: 'P8',
    blockId: 'diseno',
    kind: 'scale',
    order: 8,
    text: '¿Configura sus sistemas para recopilar el mínimo de datos por defecto (Privacy by Default)?',
    weight: 12,
    options: [
      { scale: 0, label: 'No', description: 'Al registrarse o usar un sistema, las casillas de consentimiento masivo, cookies de rastreo y transferencia de datos vienen preactivadas (óptica Opt-out agresiva).', points: 0 },
      { scale: 35, label: 'Inicial', description: 'Las plataformas se configuran bajo criterios comerciales estándar y solo se modifican si el usuario lo solicita expresamente.', points: 4.2 },
      { scale: 70, label: 'Parcial', description: 'Se han configurado medidas por defecto en canales digitales principales (ej. la web pública), pero los sistemas internos o aplicaciones móviles siguen viniendo con configuraciones permisivas por defecto.', points: 8.4 },
      { scale: 100, label: 'Total', description: 'Todas las aplicaciones e infraestructuras están configuradas para que, de forma automática e inicial, solo se procesen los datos estrictamente necesarios para la actividad, requiriendo una acción positiva del usuario (Opt-in) para cualquier tratamiento adicional.', points: 12.0 },
    ],
  },
  // P9
  {
    id: 'P9',
    blockId: 'gobernanza',
    kind: 'scale',
    order: 9,
    text: '¿Cuenta con un sistema de administración de riesgos asociados al tratamiento de datos personales?',
    weight: 16,
    options: [
      { scale: 0, label: 'No', description: 'No se identifican, miden ni gestionan los riesgos de brechas de seguridad o pérdidas de privacidad de manera estructurada.', points: 0 },
      { scale: 35, label: 'Inicial', description: 'Los riesgos de privacidad están diluidos dentro de la matriz general de riesgos tecnológicos de la empresa, sin controles específicos para datos personales.', points: 5.6 },
      { scale: 70, label: 'Parcial', description: 'Se cuenta con una matriz de riesgos específica de protección de datos, pero no se actualiza periódicamente ni cuenta con planes de acción o responsables asignados para la mitigación.', points: 11.2 },
      { scale: 100, label: 'Total', description: 'Se tiene un Sistema de Gestión de Seguridad de la Información (SGSI) o modelo de administración de riesgos vivo, con revisiones semestrales o anuales, indicadores de exposición, planes de respuesta ante incidentes y controles técnicos/operativos auditados.', points: 16.0 },
    ],
  },
  // P10
  {
    id: 'P10',
    blockId: 'gobernanza',
    kind: 'scale',
    order: 10,
    text: '¿Cuenta con un Oficial de Protección de Datos Personales (DPO / Data Protection Officer)?',
    weight: 8,
    options: [
      { scale: 0, label: 'No', description: 'No hay ninguna persona o área asignada para vigilar el cumplimiento de la privacidad.', points: 0 },
      { scale: 35, label: 'Inicial', description: 'Se asume de manera informal que el área Legal o de TI se encarga, pero ningún colaborador tiene la función asignada explícitamente dentro de su perfil laboral.', points: 2.8 },
      { scale: 70, label: 'Parcial', description: 'Se ha delegado la función a un comité interno o a un empleado como recarga de funciones, pero este no cuenta con autonomía, presupuesto ni tiempo suficiente dedicado a la tarea.', points: 5.6 },
      { scale: 100, label: 'Total', description: 'Existe un Oficial de Protección de Datos (interno o externo) designado explícitamente, con línea directa de reporte a la alta dirección, autonomía, recursos técnicos y capacidad para liderar el programa de cumplimiento.', points: 8.0 },
    ],
  },
  // P11 — Validation
  {
    id: 'P11',
    blockId: 'gobernanza',
    kind: 'validation',
    order: 11,
    text: '¿Está designado formalmente el Oficial de Protección de Datos?',
    weight: 0,
    options: [],
  },
]