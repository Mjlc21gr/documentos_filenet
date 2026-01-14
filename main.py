from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
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

async def stream_from_aws(url: str, headers: dict):
    """
    Stream de datos desde AWS para evitar timeouts
    """
    # Configuración de timeout más simple y permisiva
    timeout = httpx.Timeout(120.0)  # Solo timeout general más largo
    
    # Configuración más específica del cliente HTTP
    async with httpx.AsyncClient(
        timeout=timeout,
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=100),
        verify=False  # Para evitar problemas SSL si los hay
    ) as client:
        async with client.stream('GET', url, headers=headers) as response:
            if response.status_code == 200:
                async for chunk in response.aiter_bytes(chunk_size=8192):  # 8KB chunks
                    yield chunk
            elif response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail="Documento no encontrado"
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error en AWS API: {response.status_code}"
                )

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
        
        logger.info("Iniciando streaming directo desde AWS...")
        
        # Obtener información del archivo (usaremos valores por defecto)
        response_headers = {
            "Content-Disposition": f'attachment; filename="documento_{request.idFilenet}.pdf"'
        }
        
        logger.info(f"Iniciando streaming del documento")
        
        # Usar StreamingResponse para enviar el archivo por chunks
        return StreamingResponse(
            stream_from_aws(url, headers),
            media_type="application/pdf",  # Tipo por defecto
            headers=response_headers
        )
        
    except httpx.TimeoutException as e:
        logger.error(f"Timeout en petición a AWS: {str(e)}")
        raise HTTPException(
            status_code=504,
            detail="Timeout al consultar la API de AWS"
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

@app.get("/debug-aws/{idFilenet}")
async def debug_aws_connection(idFilenet: str):
    """
    Debug endpoint para probar conectividad específica
    """
    url = f"{AWS_API_URL}/{idFilenet}"
    
    try:
        # Test 1: Ping básico
        import socket
        hostname = "c4huz7dmpc-vpce-0d1e15f4e7cf53d97.execute-api.us-east-1.amazonaws.com"
        
        try:
            socket.gethostbyname(hostname)
            dns_status = "OK"
        except:
            dns_status = "FAILED"
        
        # Test 2: HTTP simple
        timeout = httpx.Timeout(30.0)
        async with httpx.AsyncClient(timeout=timeout) as client:
            response = await client.get(url, headers={"x-api-key": AWS_API_KEY})
            
            return {
                "url": url,
                "dns_resolution": dns_status,
                "hostname": hostname,
                "status_code": response.status_code,
                "response_time": "N/A",
                "content_length": len(response.content) if response.status_code == 200 else 0,
                "headers": dict(response.headers),
                "error": None
            }
            
    except Exception as e:
        return {
            "url": url,
            "dns_resolution": dns_status,
            "hostname": hostname,
            "status_code": None,
            "response_time": "N/A",
            "error": str(e),
            "error_type": type(e).__name__
        }

@app.get("/test-aws-connection")
async def test_aws_connection():
    """
    Prueba la conectividad básica con AWS API
    """
    try:
        timeout = httpx.Timeout(
            timeout=20.0,   # Default timeout
            connect=10.0,   # Connection timeout
            read=10.0,      # Read timeout
            write=10.0,     # Write timeout
            pool=10.0       # Pool timeout
        )
        async with httpx.AsyncClient(timeout=timeout) as client:
            # Probar con el documento conocido
            test_url = f"{AWS_API_URL}/{{60584D9B-0000-C217-968B-A1E0D75A061E}}"
            response = await client.head(test_url, headers={"x-api-key": AWS_API_KEY})
            return {
                "status": "connected",
                "aws_response_code": response.status_code,
                "content_type": response.headers.get("Content-Type"),
                "content_length": response.headers.get("Content-Length"),
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