from fastapi import FastAPI, HTTPException
from fastapi.responses import Response
from pydantic import BaseModel
import httpx
import os
from typing import Optional

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
    try:
        # Construir la URL completa - ERROR CORREGIDO AQUÍ
        url = f"{AWS_API_URL}/{request.idFilenet}"
        
        # Headers para la petición
        headers = {
            "x-api-key": AWS_API_KEY
        }
        
        # Realizar la petición a AWS con timeout extendido
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.get(url, headers=headers)
            
            # Verificar si la petición fue exitosa
            if response.status_code == 200:
                # Obtener el Content-Type de la respuesta de AWS
                content_type = response.headers.get("Content-Type", "application/octet-stream")
                
                # Devolver el mismo contenido binario que devuelve AWS
                return Response(
                    content=response.content,
                    media_type=content_type,
                    headers={
                        "Content-Disposition": f'attachment; filename="documento_{request.idFilenet}.pdf"'
                    }
                )
            elif response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Documento con ID {request.idFilenet} no encontrado"
                )
            else:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error al consultar AWS API: {response.text}"
                )
                
    except httpx.TimeoutException:
        raise HTTPException(
            status_code=504,
            detail="Timeout al consultar la API de AWS"
        )
    except httpx.RequestError as exc:
        raise HTTPException(
            status_code=503,
            detail=f"Error de conexión con AWS API: {str(exc)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

# Para desarrollo local
if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)