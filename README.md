# API FileNet Proxy - GCP

API REST desarrollada con FastAPI para consultar documentos de FileNet a través de una API de AWS, desplegada en Google Cloud Platform (Cloud Run).

## 📋 Descripción

Esta API actúa como un proxy que recibe un `idFilenet` en el body de una petición POST y consulta la API de AWS para obtener la información del documento correspondiente.

## 🚀 Endpoints

### Health Check
```bash
GET /
GET /health
```

### Consultar Documento
```bash
POST /api/v1/filenet/documento
Content-Type: application/json

{
  "idFilenet": "tu-id-filenet-aqui"
}
```

**Respuesta exitosa (200):**
```json
{
  "status": "success",
  "data": { ... },
  "message": "Documento consultado exitosamente"
}
```

## 🛠️ Instalación Local

### Requisitos
- Python 3.11+
- pip

### Pasos

1. Clonar el repositorio
```bash
git clone <tu-repositorio>
cd documentos_filenet
```

2. Crear entorno virtual
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias
```bash
pip install -r requirements.txt
```

4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

5. Ejecutar la aplicación
```bash
python main.py
```

La API estará disponible en `http://localhost:8080`

## 🐳 Docker

### Construir imagen
```bash
docker build -t filenet-api .
```

### Ejecutar contenedor
```bash
docker run -p 8080:8080 \
  -e AWS_API_URL="tu-url-aws" \
  -e AWS_API_KEY="tu-api-key" \
  filenet-api
```

## ☁️ Despliegue en GCP

### Prerequisitos
1. Tener un proyecto en GCP
2. Conectar tu repositorio a Cloud Build
3. Habilitar los siguientes APIs:
   - Cloud Run API
   - Cloud Build API
   - Container Registry API

### Configuración en GCP

1. **Ir a Cloud Build → Triggers**
2. **Crear un nuevo trigger** con estos parámetros:
   - Fuente: Tu repositorio conectado
   - Rama: `main` (o la que prefieras)
   - Archivo de configuración: `cloudbuild.yaml`

3. **Configurar las variables de sustitución** en el trigger:
   - `_AWS_API_URL`: URL de tu API de AWS
   - `_AWS_API_KEY`: Tu API Key de AWS

4. **Hacer push al repositorio** para activar el despliegue automático

### Despliegue Manual (opcional)

```bash
# Autenticarse
gcloud auth login

# Configurar proyecto
gcloud config set project TU-PROJECT-ID

# Build y deploy
gcloud builds submit --config cloudbuild.yaml
```

## 🔐 Variables de Entorno

| Variable | Descripción | Requerida |
|----------|-------------|-----------|
| AWS_API_URL | URL base de la API de AWS | Sí |
| AWS_API_KEY | API Key para autenticación en AWS | Sí |
| PORT | Puerto de la aplicación (default: 8080) | No |

## 📝 Ejemplo de Uso

```bash
# Ejemplo con curl
curl -X POST https://tu-api-gcp.run.app/api/v1/filenet/documento \
  -H "Content-Type: application/json" \
  -d '{"idFilenet": "12345"}'
```

```python
# Ejemplo con Python
import requests

url = "https://tu-api-gcp.run.app/api/v1/filenet/documento"
payload = {"idFilenet": "12345"}

response = requests.post(url, json=payload)
print(response.json())
```

## 🔧 Personalización

### Cambiar región de despliegue
Edita `cloudbuild.yaml` y cambia `us-central1` por tu región preferida.

### Ajustar recursos
En `cloudbuild.yaml` puedes modificar:
- `--memory`: Memoria asignada (ej: 256Mi, 512Mi, 1Gi)
- `--cpu`: CPUs asignadas (ej: 1, 2)
- `--max-instances`: Máximo de instancias concurrentes

## 📊 Monitoreo

Una vez desplegado en GCP, puedes monitorear tu aplicación en:
- **Cloud Run Console**: Métricas de rendimiento y logs
- **Cloud Logging**: Logs detallados de la aplicación
- **Cloud Monitoring**: Alertas y dashboards personalizados

## 🤝 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Fork el proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📄 Licencia

Este proyecto es privado y de uso interno.

## 📞 Soporte

Para soporte y preguntas, contacta al equipo de desarrollo.

