from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import httpx
import os
import logging
from typing import Optional

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuración de la aplicación
app = FastAPI(
    title="API FileNet Proxy",
    description="API para consultar documentos de FileNet a través de AWS",
    version="1.0.0"
)

# Variables de entorno
AWS_API_URL = os.getenv("AWS_API_URL", "https://c4huz7dmpc-vpce-0d1e15f4e7cf53d97.execute-api.us-east-1.amazonaws.com/stage/documentos_archivo/api/v1/filenet/documento/soporte")
AWS_API_KEY = os.getenv("AWS_API_KEY", "vvaduJRpkc85IB3MbGNo86IrfD9ssuRHa4UTgV8S")

# Modelo de entrada
class FileNetRequest(BaseModel):
    idFilenet: str

# Modelo de respuesta
class FileNetResponse(BaseModel):
    status: str
    data: Optional[dict] = None
    message: Optional[str] = None

@app.get("/")
async def root():
    """
    Endpoint raíz para verificar que la API está funcionando
    """
    return {
        "message": "API FileNet Proxy funcionando correctamente",
        "status": "OK",
        "version": "1.0.0"
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint para GCP
    """
    return {"status": "healthy"}

@app.post("/api/v1/filenet/documento")
async def consultar_documento(request: FileNetRequest):
    """
    Consulta un documento de FileNet usando el ID proporcionado y devuelve el archivo
    
    Args:
        request: Objeto con el idFilenet a consultar
        
    Returns:
        El documento (PDF, imagen, etc.) tal como lo devuelve AWS
    """
    logger.info(f"Iniciando consulta para documento ID: {request.idFilenet}")
    
    try:
        # Construir la URL completa
        url = f"{AWS_API_URL}/{request.idFilenet}"
        logger.info(f"URL construida: {url}")
        
        # Headers para la petición
        headers = {
            "x-api-key": AWS_API_KEY
        }
        
        # Configurar timeouts más largos
        timeout = httpx.Timeout(
            connect=30.0,    # 30 segundos para conectar
            read=300.0,      # 5 minutos para leer
            write=30.0,      # 30 segundos para escribir
            pool=30.0        # 30 segundos para el pool
        )
        
        logger.info("Realizando petición a AWS...")
        
        # Realizar la petición a AWS con timeout extendido
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers=headers)
            
            logger.info(f"Respuesta de AWS: {response.status_code}")
            
            # Verificar si la petición fue exitosa
            if response.status_code == 200:
                # Obtener el Content-Type de la respuesta de AWS
                content_type = response.headers.get("Content-Type", "application/octet-stream")
                content_length = len(response.content)
                
                logger.info(f"Documento encontrado. Tipo: {content_type}, Tamaño: {content_length} bytes")
                
                # Devolver el mismo contenido binario que devuelve AWS
                return Response(
                    content=response.content,
                    media_type=content_type,
                    headers={
                        "Content-Disposition": f'attachment; filename="documento_{request.idFilenet}.pdf"',
                        "Content-Length": str(content_length)
                    }
                )
            elif response.status_code == 404:
                logger.warning(f"Documento no encontrado: {request.idFilenet}")
                raise HTTPException(
                    status_code=404,
                    detail=f"Documento con ID {request.idFilenet} no encontrado"
                )
            else:
                logger.error(f"Error en AWS API: {response.status_code} - {response.text}")
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error al consultar AWS API: {response.text}"
                )
                
    except httpx.TimeoutException as e:
        logger.error(f"Timeout en petición a AWS: {str(e)}")
        raise HTTPException(
            status_code=504,
            detail=f"Timeout al consultar la API de AWS. El documento puede ser muy grande o la API está lenta."
        )
    except httpx.ConnectTimeout:
        logger.error("Timeout de conexión con AWS")
        raise HTTPException(
            status_code=503,
            detail="Timeout de conexión con AWS API"
        )
    except httpx.ReadTimeout:
        logger.error("Timeout de lectura con AWS")
        raise HTTPException(
            status_code=504,
            detail="Timeout de lectura con AWS API. El documento puede ser muy grande."
        )
    except httpx.RequestError as exc:
        logger.error(f"Error de conexión con AWS: {str(exc)}")
        raise HTTPException(
            status_code=503,
            detail=f"Error de conexión con AWS API: {str(exc)}"
        )
    except Exception as e:
        logger.error(f"Error interno: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

# Endpoint para probar la conectividad con AWS (sin documento específico)
@app.get("/test-aws-connection")
async def test_aws_connection():
    """
    Prueba la conectividad básica con AWS API
    """
    try:
        timeout = httpx.Timeout(connect=10.0, read=10.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Solo hacer un HEAD request para probar conectividad
            response = await client.head(AWS_API_URL.rsplit('/', 1)[0], 
                                       headers={"x-api-key": AWS_API_KEY})
            return {
                "status": "connected",
                "aws_response_code": response.status_code,
                "message": "Conectividad con AWS OK"
            }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error conectando con AWS: {str(e)}"
        }

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)