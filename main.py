"""
============================================================
 Lexer Aritmético — Autómata Finito Determinístico (AFD)
 Materia : Teoría de Autómatas
 Autor   : Sebastian de Jesus Cruz Cruz
 Fecha   : 2026
============================================================
"""

import sys


# ============================================================
# Tipos de token (cadenas simples)
# ============================================================
VARIABLE       = "Variable"
ENTERO         = "Entero"
REAL           = "Real"
ASIGNACION     = "Asignación"
SUMA           = "Suma"
RESTA          = "Resta"
MULTIPLICACION = "Multiplicación"
DIVISION       = "División"
POTENCIA       = "Potencia"
PAREN_ABRE     = "Paréntesis que abre"
PAREN_CIERRA   = "Paréntesis que cierra"
COMENTARIO     = "Comentario"
ERROR          = "Error"


# ============================================================
# Estados del AFD (cadenas simples)
# ============================================================
q0 = "q0"   # inicial
q1 = "q1"   # identificador / variable
q2 = "q2"   # entero
q3 = "q3"   # real (parte decimal)
q4 = "q4"   # después de E/e
q5 = "q5"   # después de E+/E-
q6 = "q6"   # dígitos del exponente


# ============================================================
# Determina si '-' debe interpretarse como signo unario
# ============================================================
def es_contexto_unario(tokens):
    if len(tokens) == 0:
        return True
    ultimo_tipo = tokens[-1][1]   # [1] = tipo de la última tupla
    if ultimo_tipo == ASIGNACION:
        return True
    if ultimo_tipo == SUMA:
        return True
    if ultimo_tipo == RESTA:
        return True
    if ultimo_tipo == MULTIPLICACION:
        return True
    if ultimo_tipo == DIVISION:
        return True
    if ultimo_tipo == POTENCIA:
        return True
    if ultimo_tipo == PAREN_ABRE:
        return True
    return False


# ============================================================
# Tokeniza una línea usando el AFD
# Cada token se guarda como tupla (valor, tipo) en la lista tokens
# ============================================================
def tokenizar_linea(linea, tokens):
    s = linea.rstrip('\r\n')
    n = len(s)
    estado = q0
    lexema = ""
    i = 0

    while i <= n:
        # Centinela: carácter ficticio que marca el fin de línea
        if i < n:
            c = s[i]
        else:
            c = '\0'

        # ---- Fin de línea: emitir lo que quede en construcción ----
        if c == '\0':
            if estado == q1:
                tokens.append((lexema, VARIABLE))
            elif estado == q2:
                tokens.append((lexema, ENTERO))
            elif estado == q3 or estado == q6:
                tokens.append((lexema, REAL))
            elif estado == q4 or estado == q5:
                tokens.append((lexema, ERROR))
            elif lexema != "":
                tokens.append((lexema, ERROR))
            break

        # ---- q0: ESTADO INICIAL ------------------------------------
        if estado == q0:

            # Espacios en blanco: ignorar
            if c == ' ' or c == '\t':
                i += 1

            # Comentario '//' — se revisa antes que la división '/'
            elif c == '/' and i + 1 < n and s[i + 1] == '/':
                tokens.append((s[i:], COMENTARIO))
                i = n

            # Operadores y símbolos de un solo carácter
            elif c == '=':
                tokens.append(('=', ASIGNACION))
                i += 1
            elif c == '+':
                tokens.append(('+', SUMA))
                i += 1
            elif c == '*':
                tokens.append(('*', MULTIPLICACION))
                i += 1
            elif c == '/':
                tokens.append(('/', DIVISION))
                i += 1
            elif c == '^':
                tokens.append(('^', POTENCIA))
                i += 1
            elif c == '(':
                tokens.append(('(', PAREN_ABRE))
                i += 1
            elif c == ')':
                tokens.append((')', PAREN_CIERRA))
                i += 1

            # '-' : puede ser unario (parte de un número) o binario (resta)
            elif c == '-':
                if i + 1 < n:
                    nxt = s[i + 1]
                else:
                    nxt = '\0'
                if i + 2 < n:
                    nxt2 = s[i + 2]
                else:
                    nxt2 = '\0'

                if es_contexto_unario(tokens) and nxt.isdigit():
                    # Ejemplo: -8  →  número negativo entero o real
                    lexema = '-'
                    i += 1
                    estado = q2
                elif es_contexto_unario(tokens) and nxt == '.' and nxt2.isdigit():
                    # Ejemplo: -.5  →  real negativo sin dígito inicial
                    lexema = '-.'
                    i += 2
                    estado = q3
                else:
                    tokens.append(('-', RESTA))
                    i += 1

            # Dígito → inicio de número entero
            elif c.isdigit():
                lexema = lexema + c
                i += 1
                estado = q2

            # Punto seguido de dígito → real sin dígito inicial (.5)
            elif c == '.' and i + 1 < n and s[i + 1].isdigit():
                lexema = '.'
                i += 1
                estado = q3

            # Letra → inicio de identificador/variable
            elif c.isalpha():
                lexema = lexema + c
                i += 1
                estado = q1

            # Carácter desconocido
            else:
                tokens.append((c, ERROR))
                i += 1

        # ---- q1: IDENTIFICADOR / VARIABLE --------------------------
        elif estado == q1:
            if c.isalpha() or c.isdigit() or c == '_':
                lexema = lexema + c
                i += 1
            else:
                tokens.append((lexema, VARIABLE))
                lexema = ""
                estado = q0
                # NO se incrementa i: el carácter se reprocesa en q0

        # ---- q2: ENTERO --------------------------------------------
        elif estado == q2:
            if c.isdigit():
                lexema = lexema + c
                i += 1
            elif c == '.':
                lexema = lexema + c
                i += 1
                estado = q3
            elif c == 'E' or c == 'e':
                lexema = lexema + c
                i += 1
                estado = q4
            else:
                tokens.append((lexema, ENTERO))
                lexema = ""
                estado = q0

        # ---- q3: REAL (parte decimal) ------------------------------
        elif estado == q3:
            if c.isdigit():
                lexema = lexema + c
                i += 1
            elif c == 'E' or c == 'e':
                lexema = lexema + c
                i += 1
                estado = q4
            else:
                tokens.append((lexema, REAL))
                lexema = ""
                estado = q0

        # ---- q4: Después de E/e (espera signo o dígito) ------------
        elif estado == q4:
            if c == '+' or c == '-':
                lexema = lexema + c
                i += 1
                estado = q5
            elif c.isdigit():
                lexema = lexema + c
                i += 1
                estado = q6
            else:
                tokens.append((lexema, ERROR))
                lexema = ""
                estado = q0

        # ---- q5: Después de E+/E- (espera dígito obligatorio) ------
        elif estado == q5:
            if c.isdigit():
                lexema = lexema + c
                i += 1
                estado = q6
            else:
                tokens.append((lexema, ERROR))
                lexema = ""
                estado = q0

        # ---- q6: Dígitos del exponente -----------------------------
        elif estado == q6:
            if c.isdigit():
                lexema = lexema + c
                i += 1
            else:
                tokens.append((lexema, REAL))
                lexema = ""
                estado = q0

        else:
            i += 1


# ============================================================
# Función principal del lexer
# ============================================================
def lexer_aritmetico(archivo):
    try:
        f = open(archivo, 'r', encoding='utf-8')
        lineas = f.readlines()
        f.close()
    except FileNotFoundError:
        print("Error: no se pudo abrir el archivo '" + archivo + "'")
        return

    tokens = []

    for linea in lineas:
        tokenizar_linea(linea, tokens)

    # Imprimir tabla de tokens
    W = 32
    encabezado_token = "Token"
    encabezado_tipo  = "Tipo"
    print(encabezado_token + " " * (W - len(encabezado_token)) + encabezado_tipo)
    print("-" * (W + 28))

    for valor, tipo in tokens:
        espacios = W - len(valor)
        if espacios < 1:
            espacios = 1
        print(valor + " " * espacios + tipo)


# ============================================================
# Entry point
# ============================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python " + sys.argv[0] + " <archivo.txt>")
    else:
        lexer_aritmetico(sys.argv[1])
