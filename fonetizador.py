import re

def texto_a_fonemas(texto):
    # Limpieza inicial
    texto = texto.lower().strip()
    fonemas_encontrados = []
    
    # REGLAS DE SUSTITUCIÓN (El orden es vital: de lo más largo a lo más corto)
    sustituciones = [
        # Palabras completas o sílabas de 3 letras (Prioridad máxima)
        ('que', 'que'), ('qui', 'que'), 
        ('che', 'che'), ('rre', 'rre'), ('lle', 'lle'),
        
        # Fonemas de 2 letras (Prioridad media)
        ('es', 'es'), ('er', 'er'), ('el', 'el'), # <--- Ahora se detectan correctamente
        ('ce', 'es'), ('ci', 'es'), 
        ('ca', 'que'), ('co', 'que'), ('cu', 'que'),
        ('ga', 'gue'), ('go', 'gue'), ('gu', 'gue'),
        ('ge', 'je'), ('gi', 'je'),
        ('rr', 'rre'), ('ll', 'lle'),
        
        # Letras individuales (Prioridad baja)
        ('z', 'ze'), ('k', 'que'), ('j', 'je'),
        ('v', 've'), ('f', 'fe'), ('b', 'be'), ('p', 'pe'),
        ('d', 'de'), ('t', 'te'), ('m', 'me'), ('n', 'ne'),
        ('ñ', 'ñe'), ('r', 're'), ('l', 'le'), ('s', 'es')
    ]
    
    # ALGORITMO DE BÚSQUEDA GEOMÉTRICA
    i = 0
    while i < len(texto):
        match_encontrado = False
        
        for patron, fonema in sustituciones:
            # Comprueba si el texto en la posición 'i' empieza con el patrón
            if texto.startswith(patron, i):
                fonemas_encontrados.append(fonema)
                i += len(patron)
                match_encontrado = True
                break
        
        if not match_encontrado:
            # Si no es una consonante conocida (es una vocal), saltamos a la siguiente letra
            i += 1 
            
    return fonemas_encontrados

# --- ÁREA DE PRUEBAS ---
if __name__ == "__main__":
    test_palabras = ["que", "fe", "es", "nene", "casa"]
    for p in test_palabras:
        print(f"Palabra: {p} -> Fonemas: {texto_a_fonemas(p)}")