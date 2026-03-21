# Sistema de Interpretación y Optimización de Planos Estructurales

Este monorepo contiene la arquitectura escalable y distribuida de un sistema avanzado de Machine Learning capaz de interpretar, generar y optimizar detalles estructurales de vigas y acero de refuerzo a partir de planos CAD y PDFs.

## 🏗️ Arquitectura de Microservicios

El sistema está diseñado bajo un enfoque estricto de microservicios, separando la inferencia de ML de la interfaz de usuario y la lógica de negocio.

1.  **Frontend (`/frontend`) - Next.js (App Router)**
    *   **Tecnologías:** React 19, TypeScript, Tailwind CSS, Zod.
    *   **Responsabilidad:** Proveer una interfaz de usuario inmersiva para la carga de planos. Uso exclusivo de Server Components y Server Actions para manejo de estado y mutaciones (ej. la subida de archivos está implementada como un Server Action seguro con manejo de `try/catch`).
2.  **Orquestador (`/orchestrator`) - Node.js (BFF)**
    *   **Tecnologías:** Express.js, TypeScript.
    *   **Responsabilidad:** Backend-for-Frontend. Gestiona el enrutamiento, la autenticación y actúa como intermediario seguro entre el frontend y el motor de IA. Toda operación asíncrona está envuelta en bloques `try/catch`.
3.  **Motor ML (`/ml_engine`) - Python (FastAPI)**
    *   **Tecnologías:** FastAPI, Pydantic, ezdxf, Uvicorn.
    *   **Responsabilidad:** Procesamiento intensivo, inferencia de modelos y pipelines de ingesta de datos. Extrae la geometría vectorial (`ezdxf`), la valida rígidamente con Pydantic y expone una API REST para comunicarse con el orquestador. Las excepciones (`try/except`) son obligatorias.

## 🧠 Arquitectura del Modelo de IA

El núcleo del sistema emplea un enfoque de inteligencia artificial híbrida:
*   **Comprensión:** Se utilizan Redes Neuronales de Grafos (GNN) para interpretar la relación espacial y topología de los datos vectoriales extraídos (líneas, polígonos). Para los planos rasterizados, se emplean CNNs o Vision Transformers.
*   **Generación:** Se integran Modelos Generativos (Diffusion Models o GANs) que proponen nuevas configuraciones de armado de vigas basándose en la topología leída.
*   **Optimización:** Mediante Aprendizaje por Refuerzo (Reinforcement Learning), el sistema es recompensado si el diseño propuesto minimiza el acero, mantiene la resistencia y cumple códigos de construcción.

## 🛡️ Reglas y Estándares de Implementación
*   **Tipado Estricto:** Obligatorio TypeScript en JS y Type Hints en Python.
*   **Manejo de Excepciones:** Todo proceso I/O y de inferencia DEBE contener un bloque `try/catch` (JS) o `try/except` (Python). No se admiten silencios sin log o manejo.
*   **Validación Fronteriza:** Todos los inputs que ingresan a un microservicio se validan con esquemas (Zod en Next.js, Pydantic en FastAPI).

## 🚀 Cómo Iniciar

### 1. Motor ML (FastAPI)
```bash
cd ml_engine
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### 2. Orquestador (Node.js)
```bash
cd orchestrator
npm install
npm run dev
```

### 3. Frontend (Next.js)
```bash
cd frontend
npm install
npm run dev
```
