import re

def texto_a_fonemas(texto):
    texto = texto.lower().strip()
    
    # Reglas de sustitución para que coincidan con tu tabla
    # El orden importa: de lo más complejo a lo más simple
    sustituciones = [
        ('che', 'che'), ('rr', 'rre'), ('ll', 'lle'),
        ('ce', 'es'), ('ci', 'es'), ('z', 'ze'),
        ('ca', 'que'), ('co', 'que'), ('cu', 'que'), ('k', 'que'),
        ('ga', 'gue'), ('go', 'gue'), ('gu', 'gue'),
        ('ge', 'je'), ('gi', 'je'), ('j', 'je'),
        ('v', 've'), ('f', 'fe'), ('b', 'be'), ('p', 'pe'),
        ('d', 'de'), ('t', 'te'), ('m', 'me'), ('n', 'ne'),
        ('ñ', 'ñe'), ('r', 're'), ('l', 'le'), ('s', 'es')
    ]
    
    fonemas_encontrados = []
    
    # Procesamos la palabra buscando coincidencias de fonemas
    i = 0
    while i < len(texto):
        match_encontrado = False
        for patron, fonema in sustituciones:
            if texto.startswith(patron, i):
                fonemas_encontrados.append(fonema)
                i += len(patron)
                match_encontrado = True
                break
        if not match_encontrado:
            i += 1 # Ignorar caracteres que no son consonantes (vocales se manejan aparte)
            
    return fonemas_encontrados

# Prueba rápida: "casa" -> ['que', 'es']