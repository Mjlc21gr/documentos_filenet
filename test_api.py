"""
Script de prueba para la API de FileNet
Consulta directamente la API de AWS
"""
import requests
import json

# Configuración de AWS API
AWS_API_URL = "https://c4huz7dmpc-vpce-0d1e15f4e7cf53d97.execute-api.us-east-1.amazonaws.com/stage/documentos_archivo/api/v1/filenet/documento/soporte"
AWS_API_KEY = "vvaduJRpkc85IB3MbGNo86IrfD9ssuRHa4UTgV8S"
TEST_ID_FILENET = "{60584D9B-0000-C217-968B-A1E0D75A061E}"

def test_consultar_documento(id_filenet):
    """Consulta directamente el documento en la API de AWS"""
    print(f"🔍 Consultando documento con ID: {id_filenet}")
    try:
        # Construir la URL completa
        url = f"{AWS_API_URL}/{id_filenet}"
        
        # Headers con la API key
        headers = {
            "x-api-key": AWS_API_KEY
        }
        
        print(f"📤 Enviando GET a: {url}")
        print(f"🔑 Usando x-api-key")
        
        response = requests.get(url, headers=headers, timeout=30)
        
        print(f"\n✅ Status Code: {response.status_code}")
        
        if response.status_code == 200:
            # Obtener información del contenido
            content_type = response.headers.get('Content-Type', 'unknown')
            content_length = len(response.content)
            content_disposition = response.headers.get('Content-Disposition', 'N/A')
            
            print(f"📄 Content-Type: {content_type}")
            print(f"📦 Tamaño: {content_length:,} bytes ({content_length/1024:.2f} KB)")
            print(f"📎 Content-Disposition: {content_disposition}")
            
            print("\n📋 Headers recibidos:")
            print("="*60)
            for key, value in response.headers.items():
                print(f"  {key}: {value}")
            
            print("="*60)
            print("✅ ¡ÉXITO! La API respondió correctamente con el documento")
            print("   El documento se puede descargar directamente desde la API")
            print("="*60)
            
            return True
        else:
            print(f"❌ Error: Status code {response.status_code}")
            print(f"📄 Respuesta: {response.text}")
            return False
    except requests.exceptions.Timeout:
        print("❌ Error: Timeout - La petición tardó demasiado")
        return False
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar a la API. ¿Está ejecutándose?")
        return False
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        try:
            print(f"📄 Respuesta de error: {response.text}")
        except:
            pass
        return False

def main():
    """Ejecuta todas las pruebas"""
    print("="*60)
    print("🚀 INICIANDO PRUEBAS DE LA API DE AWS FILENET")
    print("="*60)
    print(f"🌐 URL Base: {AWS_API_URL}")
    print(f"🆔 ID de prueba: {TEST_ID_FILENET}")
    print("="*60)
    
    # Lista de pruebas
    tests = [
        ("Consultar Documento en AWS", lambda: test_consultar_documento(TEST_ID_FILENET))
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Error inesperado en {test_name}: {str(e)}")
            results.append((test_name, False))
    
    # Resumen
    print("\n" + "="*60)
    print("📊 RESUMEN DE PRUEBAS")
    print("="*60)
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    total_tests = len(results)
    passed_tests = sum(1 for _, result in results if result)
    print(f"\n📈 Total: {passed_tests}/{total_tests} pruebas exitosas")
    print("="*60)

if __name__ == "__main__":
    print("\n💡 NOTA: Este script consultará directamente la API de AWS")
    print(f"   URL: {AWS_API_URL}\n")
    
    input("Presiona Enter para continuar con las pruebas...")
    main()

