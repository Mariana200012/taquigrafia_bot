import re

def obtener_posicion(texto):
    """Detecta la primera vocal para determinar la posición de toda la palabra."""
    vocal = next((c for c in texto.lower() if c in 'aeiou'), 'e')
    if vocal in ['a', 'i']:
        return 1  # 1ª Posición: Arriba
    elif vocal in ['e', 'o']:
        return 2  # 2ª Posición: En la línea
    elif vocal in ['u']:
        return 3  # 3ª Posición: Atravesando
    return 2

def texto_a_fonemas(texto):
    texto = texto.lower().strip()
    posicion = obtener_posicion(texto) # Calculamos posición una vez por palabra
    fonemas_encontrados = []
    
    sustituciones = [
        ('que', 'que'), ('qui', 'que'), ('che', 'che'), ('rre', 'rre'), ('lle', 'lle'),
        ('es', 'es'), ('er', 'er'), ('el', 'el'), ('ce', 'es'), ('ci', 'es'), 
        ('ca', 'que'), ('co', 'que'), ('cu', 'que'), ('ga', 'gue'), ('go', 'gue'), 
        ('gu', 'gue'), ('ge', 'je'), ('gi', 'je'), ('rr', 'rre'), ('ll', 'lle'),
        ('z', 'ze'), ('k', 'que'), ('j', 'je'), ('v', 've'), ('f', 'fe'), ('b', 'be'), 
        ('p', 'pe'), ('d', 'de'), ('t', 'te'), ('m', 'me'), ('n', 'ne'), ('ñ', 'ñe'), 
        ('r', 're'), ('l', 'le'), ('s', 'es')
    ]
    
    i = 0
    while i < len(texto):
        match_encontrado = False
        for patron, fonema in sustituciones:
            if texto.startswith(patron, i):
                # Ahora guardamos el fonema con su posición
                fonemas_encontrados.append({'sonido': fonema, 'posicion': posicion})
                i += len(patron)
                match_encontrado = True
                break
        if not match_encontrado:
            i += 1 
            
    return fonemas_encontrados

if __name__ == "__main__":
    test = "taco"
    print(f"Palabra: {test} -> {texto_a_fonemas(test)}")