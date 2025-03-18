import requests
import xml.etree.ElementTree as ET
from requests.auth import HTTPDigestAuth
import urllib3
import sys
import json

# Desactivar advertencias de certificados SSL
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

def get_device_info(ip, username, password, port=80):
    """
    Obtiene información general del grabador Hikvision

    Args:
        ip: Dirección IP del grabador
        username: Nombre de usuario para autenticación
        password: Contraseña para autenticación
        port: Puerto HTTP (por defecto 80)

    Returns:
        Diccionario con información del dispositivo o mensaje de error
    """
    url = f"http://{ip}:{port}/ISAPI/System/deviceInfo"
    auth = HTTPDigestAuth(username, password)

    print(f"Consultando información del dispositivo en: {url}")

    try:
        response = requests.get(url, auth=auth, timeout=10)
        print(f"Código de respuesta: {response.status_code}")

        if response.status_code == 200:

            # Parsear la respuesta XML
            try:
                root = ET.fromstring(response.content)
                device_info = parse_device_info(root)
                return {
                    'status': 'success',
                    'device_info': device_info,
                    'raw_response': response.text
                }
            except ET.ParseError as e:
                return {
                    'status': 'error',
                    'message': f"Error al parsear XML: {str(e)}",
                    'raw_response': response.text
                }
        else:
            return {
                'status': 'error',
                'message': f"Error HTTP: {response.status_code}",
                'details': response.text if hasattr(response, 'text') else "No hay detalles"
            }

    except requests.exceptions.RequestException as e:
        return {
            'status': 'error',
            'message': f"Error de conexión: {str(e)}"
        }


def parse_device_info(root):
    """
    Extrae la información del dispositivo del XML de respuesta
    """
    # Lista de campos comunes en deviceInfo (actualizada con los campos del XML recibido)
    fields = [
        'deviceName', 'deviceID', 'deviceDescription', 'deviceLocation',
        'deviceStatus', 'deviceType', 'model', 'serialNumber',
        'macAddress', 'firmwareVersion', 'firmwareReleasedDate',
        'bootVersion', 'bootReleasedDate', 'hardwareVersion',
        'encoderVersion', 'encoderReleasedDate', 'deviceLanguage',
        'channelNums', 'analogChannelNums', 'digitalChannelNums',
        'videoInNums', 'videoOutNums', 'bitRate', 'bitRateType',
        'resolution', 'frameRate', 'eventLog', 'supportFTP', 'supportddns',
        'supportEmail', 'supportNTP', 'supportPPPoE', 'supportWireless',
        'supportIPv6', 'systemContact', 'telecontrolID', 'supportBeep',
        'supportVideoLoss', 'firmwareVersionInfo', 'manufacturer',
        'subSerialNumber', 'OEMCode'
    ]

    device_info = {}

    # Manejar namespace si existe
    namespace = ''
    if '}' in root.tag:
        namespace = root.tag.split('}', 1)[0] + '}'

    # Extraer todos los campos disponibles
    for field in fields:
        # Buscar con namespace si existe
        element = root.find(f'.//{namespace}{field}') if namespace else root.find(f'.//{field}')
        if element is not None and element.text:
            device_info[field] = element.text

    # También extraer cualquier otro elemento que no esté en la lista pero exista en el XML
    for child in root:
        tag = child.tag
        # Eliminar el namespace si existe
        if '}' in tag:
            tag = tag.split('}', 1)[1]

        if tag not in device_info and child.text and child.text.strip():
            device_info[tag] = child.text.strip()

    return device_info


def format_device_info(device_info):
    """
    Formatea la información del dispositivo para presentarla de manera legible
    """
    if not device_info:
        return "No se encontró información del dispositivo"

    # Ordenar los campos para una presentación más lógica
    priority_fields = [
        'deviceName', 'model', 'deviceType', 'serialNumber', 'subSerialNumber',
        'manufacturer', 'firmwareVersion', 'hardwareVersion', 'deviceStatus',
        'deviceLocation', 'macAddress', 'deviceID', 'systemContact'
    ]

    output = ["=== INFORMACIÓN DEL DISPOSITIVO ==="]

    # Primero mostrar campos prioritarios (solo si existen)
    for field in priority_fields:
        if field in device_info:
            output.append(f"{field}: {device_info[field]}")

    # Agrupar información de firmware
    output.append("\n=== INFORMACIÓN DE FIRMWARE ===")
    firmware_fields = [
        'firmwareVersion', 'firmwareReleasedDate', 'firmwareVersionInfo',
        'encoderVersion', 'encoderReleasedDate', 'bootVersion', 'bootReleasedDate'
    ]

    for field in firmware_fields:
        if field in device_info and field != 'firmwareVersion':  # Evitar duplicar firmwareVersion
            output.append(f"{field}: {device_info[field]}")

    # Luego mostrar el resto de campos
    output.append("\n=== INFORMACIÓN ADICIONAL ===")
    for key, value in sorted(device_info.items()):
        if key not in priority_fields and key not in firmware_fields:
            output.append(f"{key}: {value}")

    return "\n".join(output)


def save_results_to_file(result, filename="device_info_result.json"):
    """
    Guarda los resultados en un archivo JSON
    """
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
    print(f"Resultados guardados en '{filename}'")


if __name__ == "__main__":
    # Obtener argumentos de línea de comandos
    if len(sys.argv) < 4:
        print("Uso: python hikvision_device_info.py <IP> <usuario> <contraseña> [puerto]")
        print("Ejemplo: python3 hikvision_device_info.py 192.168.1.100 admin passw 80")
        sys.exit(1)

    ip = sys.argv[1]
    username = sys.argv[2]
    password = sys.argv[3]
    port = int(sys.argv[4]) if len(sys.argv) > 4 else 80

    print(f"Consultando información del grabador Hikvision en {ip}:{port}...")

    result = get_device_info(ip, username, password, port)

    if result['status'] == 'success':
        print("\n" + format_device_info(result['device_info']))
        # Guardar resultados en archivos
        save_results_to_file(result)
    else:
        print(f"\nError: {result['message']}")
        if 'details' in result:
            print(f"Detalles: {result['details']}")

        print("\nSugerencias:")
        print("1. Verifique que la IP y el puerto son correctos")
        print("2. Compruebe las credenciales de usuario y contraseña")
        print("3. Asegúrese de que el dispositivo es accesible en la red")
        print("4. Pruebe con diferentes puertos (80, 8000)")
        print("5. Verifique si el dispositivo requiere HTTPS en lugar de HTTP")
