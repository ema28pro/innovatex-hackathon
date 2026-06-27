# Descripción de la Solución

Nuestra plataforma resuelve este reto transformando un proceso de auditoría legal tedioso, manual y costoso en una experiencia digital, automatizada y guiada por Inteligencia Artificial.

La solución no se limita a ser un simple formulario; actúa como un **consultor virtual** que acompaña al usuario durante todo el proceso de evaluación.

## Funcionalidades Principales

### 1. Diagnostica
Evalúa el estado de cumplimiento de la empresa mediante un cuestionario estructurado dividido en **10 dimensiones clave** relacionadas con la protección de datos personales.

### 2. Educa
Explica en tiempo real la terminología jurídica y los conceptos técnicos de la Ley 1581 de 2012 utilizando un lenguaje claro y comprensible.

### 3. Cuantifica
Calcula automáticamente el nivel de madurez de la organización mediante una matriz de evaluación con una escala de **0% a 100%**, permitiendo conocer el estado actual de cumplimiento.

### 4. Resuelve
Genera automáticamente un **Plan de Acción** priorizado para cerrar las brechas de cumplimiento detectadas durante el diagnóstico.

---

# Arquitectura, Lenguajes y Tecnologías

La plataforma ha sido diseñada bajo una **arquitectura cliente-servidor desacoplada**, permitiendo escalabilidad, mantenibilidad y facilidad para incorporar nuevas funcionalidades.

---

# Capa Frontend (Interfaz de Usuario)

## Arquitectura

- Single Page Application (SPA) responsiva.

## Tecnologías

- React.js
- TypeScript
- Vite

Estas tecnologías permiten tiempos de carga reducidos y una experiencia de usuario fluida.

## Estilos e Interfaz

- Tailwind CSS
- shadcn/ui

La combinación de ambas herramientas proporciona una interfaz moderna, limpia, accesible y con apariencia corporativa, incluyendo componentes como:

- Dashboard interactivo
- Gráficos de radar
- Modales
- Tarjetas informativas

## Gestión de Estado

Se utiliza **Zustand** para administrar de manera ligera y eficiente:

- Estado del cuestionario
- Progreso del usuario
- Información de la sesión

## Seguridad y Autenticación

Integración con **Supabase Authentication**, permitiendo:

- Registro de usuarios
- Inicio de sesión
- Persistencia segura de sesiones
- Gestión de autenticación directamente desde el navegador

---

# Capa Backend (API)

## Arquitectura

API REST desarrollada bajo un modelo asíncrono con soporte **Multi-tenant**.

## Tecnologías

- Python
- FastAPI

FastAPI fue seleccionado debido a la experiencia del equipo y por ofrecer:

- Alto rendimiento
- Validación automática
- Documentación OpenAPI
- Desarrollo rápido

## Seguridad

El backend implementa:

- Validación de tokens JWT emitidos por Supabase.
- Verificación de identidad y permisos en cada solicitud.
- Protección de rutas privadas.
- Limpieza y validación de entradas del usuario.
- Cumplimiento de buenas prácticas de seguridad basadas en OWASP.

---

# Capa de Datos

## Base de Datos

La plataforma utiliza **Supabase** como Backend-as-a-Service (BaaS), basado en PostgreSQL.

Esto proporciona:

- Integridad referencial
- Alta disponibilidad
- Escalabilidad
- Excelente rendimiento

## Seguridad de Datos

Se aprovechan las políticas **Row Level Security (RLS)** para garantizar que:

- Cada empresa solo pueda acceder a su propia información.
- Los usuarios únicamente visualicen los recursos autorizados.

## Integración

La comunicación con la base de datos se realiza mediante:

- SDK oficial de Supabase
- API Data REST
- Integración desde React y FastAPI

---

# Capa de Inteligencia Artificial

## Arquitectura Agnóstica

La plataforma implementa el patrón **Adapter/Protocol** en Python.

Este diseño permite intercambiar fácilmente el proveedor del modelo de lenguaje sin modificar la lógica del negocio.

Actualmente es compatible con proveedores como:

- OpenAI
- Anthropic
- Gemini

---

# Funcionalidades Diferenciadoras

Aunque existen herramientas tradicionales basadas en listas de verificación, nuestra plataforma incorpora funcionalidades que agregan valor durante todo el proceso de cumplimiento.

---

# Asistencia Activa mediante Inteligencia Artificial

La IA acompaña al usuario durante todo el diagnóstico.

## Explicar

Traduce automáticamente los términos legales de la Ley 1581 a un lenguaje sencillo adaptado al contexto de la empresa.

## Sugerir

Analiza la información previamente registrada (sector, tamaño y respuestas anteriores) para proponer respuestas y agilizar el diligenciamiento del cuestionario.

## Recomendar

Al finalizar el diagnóstico, la IA analiza las brechas detectadas y genera recomendaciones personalizadas, priorizadas y orientadas a la mejora continua.

---

# Del Diagnóstico al Plan de Acción

La mayoría de soluciones finalizan el proceso entregando un reporte.

Nuestra plataforma transforma automáticamente los hallazgos del diagnóstico en un **Plan de Acción ejecutable**, permitiendo:

- Asignar responsables.
- Definir estados de avance.
- Registrar observaciones.
- Dar seguimiento continuo al cumplimiento.

Estados disponibles:

- Pendiente
- En progreso
- Completado

---

# Arquitectura Multi-tenant Segura

La solución fue diseñada desde su concepción como una plataforma SaaS multiempresa.

Las principales características son:

- Separación completa de datos entre organizaciones.
- Protección mediante políticas RLS de Supabase.
- Middleware Multi-tenant en FastAPI.
- Soporte para múltiples roles de usuario con permisos granulares.

---

# Sistema de Puntuación y Matriz de Madurez

Además del porcentaje de cumplimiento, la plataforma clasifica automáticamente a cada organización dentro de un modelo de madurez compuesto por cinco niveles:

| Nivel | Descripción |
|-------|-------------|
| Inexistente | No existen controles implementados. |
| Inicial | Existen esfuerzos aislados. |
| Parcial | Se cumplen algunos requisitos, pero aún existen brechas importantes. |
| Implementado | La mayoría de controles se encuentran implementados. |
| Optimizado | La organización aplica buenas prácticas y mejora continuamente. |

Toda esta información se presenta mediante un Dashboard interactivo que incluye:

- Indicadores visuales.
- Gráficos de radar.
- Evolución histórica.
- Comparación entre evaluaciones.

---

# Experiencia de Usuario

La plataforma fue diseñada para minimizar la fricción durante el uso.

## Guardado Automático

Cada respuesta es almacenada automáticamente en segundo plano, evitando pérdida de información.

## Reportes Ejecutivos

Permite generar reportes completos en formato PDF que pueden ser compartidos con directivos, auditores o responsables del cumplimiento.

---

# Resumen de Tecnologías

| Capa | Tecnologías |
|------|-------------|
| Frontend | React.js, TypeScript, Vite, Tailwind CSS, shadcn/ui, Zustand |
| Backend | Python, FastAPI |
| Base de Datos | Supabase (PostgreSQL), Row Level Security |
| Autenticación | Supabase Auth, JWT |
| Inteligencia Artificial | Arquitectura Adapter/Protocol compatible con OpenAI, Anthropic y Gemini |
| Seguridad | OWASP, JWT, RLS, Middleware Multi-tenant |
