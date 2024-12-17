import math
import json
import os

def leer_datos_entrada(archivo):
    """
    Lee la información de entrada desde un archivo JSON.
    :param archivo: Nombre del archivo JSON.
    :return: Diccionario con los datos de entrada.
    """
    if not os.path.exists(archivo):
        raise FileNotFoundError(f"El archivo '{archivo}' no se encuentra en el directorio actual: {os.getcwd()}")
    with open(archivo, 'r') as file:
        datos = json.load(file)
    return datos

def calcular_mrsg_subgrade(CBR):
    """
    Calcula el Módulo Resiliente de la Subgrade (MRSG) basado en el CBR.
    :param CBR: Relación de soporte de California en %.
    :return: Valor MRSG (psi).
    """
    print("\nCalculando MRSG (Módulo Resiliente de la Subgrade)...")
    print(f"CBR ingresado: {CBR:.2f}%")
    MRSG = 1945 * (CBR ** 0.684)  # Relación ajustada empíricamente
    print(f"MRSG calculado: {MRSG:.2f} psi")
    return round(MRSG, 2)

def calcular_k_subestructura_psi_in(MRSG, resilient_modulus_base, espesor_base):
    """
    Calcula el K-Value de la subestructura compuesto, considerando subgrade y base granular, en psi/in.
    :param MRSG: Módulo resiliente de la subgrade (psi).
    :param resilient_modulus_base: Módulo resiliente de la base granular (psi).
    :param espesor_base: Espesor de la base granular (pulgadas).
    :return: K-Value de la subestructura (psi/in).
    """
    print("\nCalculando K-Value de la subestructura en psi/in...")
    k_subgrade_psi_in = MRSG / 10.0  # Relación de conversión ajustada a psi/in
    k_base_psi_in = resilient_modulus_base / (espesor_base ** 0.5)
    k_total_psi_in = k_subgrade_psi_in + k_base_psi_in
    print(f"K-Value de subgrade: {k_subgrade_psi_in:.2f} psi/in")
    print(f"K-Value adicional de base granular: {k_base_psi_in:.2f} psi/in")
    print(f"K-Value total de subestructura: {k_total_psi_in:.2f} psi/in")
    return round(k_total_psi_in, 2)

def calcular_espesor_losa_rigida(ESALs, ZR, So, Sc, Cd, Ec, k, delta_PSI):
    """
    Calcula el espesor de la losa de un pavimento rígido según AASHTO 93.
    :param ESALs: Número de aplicaciones de carga equivalente (18-kip ESALs).
    :param ZR: Factor de confiabilidad (Z-score).
    :param So: Desviación estándar combinada.
    :param Sc: Módulo de rotura del concreto (psi).
    :param Cd: Coeficiente de transferencia de carga.
    :param Ec: Módulo de elasticidad del concreto (psi).
    :param k: Módulo de reacción compuesto total (psi/in).
    :param delta_PSI: Diferencia entre índice de serviciabilidad inicial y terminal.
    :return: Espesor de losa (en pulgadas).
    """
    print("\nCalculando espesor de losa rígida...")
    A = ZR * So  # Factor de confiabilidad
    B = 7.35 * math.log10(ESALs + 1) - 0.06
    C = (Sc * Cd) / (k ** 0.25)
    
    # Término adicional
    D1 = (4.22 - 0.32 * delta_PSI) * math.log10(ESALs)
    D2 = (215.63 * math.sqrt(C)) - 18.42
    
    # Iteración para ajustar el espesor de losa
    espesor_inicial = 7.0  # Valor inicial aproximado
    for _ in range(10):
        espesor_inicial = ((A + B) / (D1 + D2)) ** (1 / 1.132)
    print(f"Espesor calculado de losa: {espesor_inicial:.2f} pulgadas")
    return round(espesor_inicial, 2)

def main():
    # Buscar el archivo de entrada en el directorio actual
    archivo_entrada = "datos_entrada.json"
    print(f"Leyendo datos desde el archivo: {archivo_entrada}\n")
    
    try:
        # Leer los datos de entrada
        datos = leer_datos_entrada(archivo_entrada)
        
        # Extraer valores de entrada
        ESALs = datos['Traffic']['ESALs']
        ZR = -1.645  # Factor Z para 95% de confiabilidad
        So = 0.39  # Desviación estándar fija según AASHTO
        Sc = datos['Concrete']['FlexuralStrength']
        Cd = 1.0  # Transferencia de carga fija
        Ec = datos['Concrete']['ModulusOfElasticity']
        CBR = datos['Subgrade']['CBR']
        delta_PSI = 2.0  # Diferencia de serviciabilidad fija
        resilient_modulus_base = datos['Structure']['ResilientModulus']
        espesor_base = datos['Structure']['LayerThickness']

        # Cálculos de subgrade y base granular
        MRSG = calcular_mrsg_subgrade(CBR)
        k_total_psi_in = calcular_k_subestructura_psi_in(MRSG, resilient_modulus_base, espesor_base)

        # Calcular espesor de losa
        espesor_losa = calcular_espesor_losa_rigida(ESALs, ZR, So, Sc, Cd, Ec, k_total_psi_in, delta_PSI)
        
        # Imprimir resultados finales
        print("\nRESULTADOS FINALES:")
        print(f"CBR ingresado: {CBR}%")
        print(f"Módulo Resiliente de Subgrade (MRSG): {MRSG} psi")
        print(f"K-Value total de subestructura: {k_total_psi_in} psi/in")
        print(f"Espesor final de losa requerida: {espesor_losa} pulgadas")
    
    except FileNotFoundError as e:
        print(e)
        print("Asegúrese de que el archivo 'datos_entrada.json' esté en el mismo directorio o proporcione la ruta correcta.")
    except KeyError as e:
        print(f"Error: Clave faltante en el archivo de entrada - {e}")
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")

if __name__ == "__main__":
    main()
