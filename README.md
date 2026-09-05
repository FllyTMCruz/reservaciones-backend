# Sistema de Reservaciones - Backend (API RESTful)

Núcleo lógico y de alto rendimiento del Sistema de Reservaciones. Procesa las operaciones CRUD, valida datos estrictamente y maneja la concurrencia de múltiples usuarios[cite: 2]. La arquitectura está preparada para contenedorización con Docker[cite: 2].

## 🚀 Características
* **Gestión de Citas (CRUD):** Lógica principal y manejo de espacios de tiempo, a cargo de Dev2[cite: 1].
* **Validación Estricta:** Modelado de datos (fechas, IDs, textos) mediante Pydantic antes de la inserción en base de datos[cite: 2].
* **Seguridad y Persistencia:** Autenticación por tokens JWT y persistencia en Supabase (PostgreSQL) gestionados por Dev3[cite: 1, 2].

## 🛠️ Stack Tecnológico
* **Framework:** FastAPI[cite: 2].
* **Lenguaje:** Python[cite: 2].
* **Base de Datos & Auth:** Supabase (PostgreSQL + JWT Auth)[cite: 2].
* **Infraestructura:** Docker y DigitalOcean (Droplet o App Platform)[cite: 2].

## ⚙️ Desarrollo Local
1. Clonar el repositorio.
2. Crear un entorno virtual e instalar las dependencias con `pip install -r requirements.txt`.
3. Configurar variables de entorno para la conexión con Supabase.
4. Ejecutar el servidor con `uvicorn app.main:app --reload`.
