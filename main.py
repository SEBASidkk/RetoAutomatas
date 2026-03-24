"""
============================================================
 Lexer Aritmético — Autómata Finito Determinístico (AFD)
 Materia : Teoría de Autómatas
 Autor   : Sebastian de Jesus Cruz Cruz
 Fecha   : 2026
============================================================
"""

import sys
from enum import Enum, auto


# ============================================================
# Tipos de token
# ============================================================
class TokenType(Enum):
    VARIABLE        = auto()
    ENTERO          = auto()
    REAL            = auto()
    ASIGNACION      = auto()
    SUMA            = auto()
    RESTA           = auto()
    MULTIPLICACION  = auto()
    DIVISION        = auto()
    POTENCIA        = auto()
    PAREN_ABRE      = auto()
    PAREN_CIERRA    = auto()
    COMENTARIO      = auto()
    ERROR           = auto()


NOMBRE_TIPO = {
    TokenType.VARIABLE:       "Variable",
    TokenType.ENTERO:         "Entero",
    TokenType.REAL:           "Real",
    TokenType.ASIGNACION:     "Asignacion",
    TokenType.SUMA:           "Suma",
    TokenType.RESTA:          "Resta",
    TokenType.MULTIPLICACION: "Multiplicacion",
    TokenType.DIVISION:       "Division",
    TokenType.POTENCIA:       "Potencia",
    TokenType.PAREN_ABRE:     "Parentesis que abre",
    TokenType.PAREN_CIERRA:   "Parentesis que cierra",
    TokenType.COMENTARIO:     "Comentario",
    TokenType.ERROR:          "Error",
}


# Token es simplemente una tupla nombrada
class Token:
    def __init__(self, valor: str, tipo: TokenType):
        self.valor = valor
        self.tipo  = tipo


# ============================================================
# Estados del AFD
# ============================================================
class Estado(Enum):
    q0 = 0   # START
    q1 = 1   # IDENTIFICADOR
    q2 = 2   # ENTERO
    q3 = 3   # REAL (parte decimal)
    q4 = 4   # Después de E/e (espera signo o dígito de exponente)
    q5 = 5   # Después de E+/E- (espera dígitos de exponente)
    q6 = 6   # Dígitos del exponente
    q7 = 7   # COMENTARIO


# ============================================================
# Determina si '-' debe interpretarse como signo unario
# ============================================================
def es_contexto_unario(tokens: list) -> bool:
    if not tokens:
        return True
    last = tokens[-1].tipo
    return last in (
        TokenType.ASIGNACION,
        TokenType.SUMA,
        TokenType.RESTA,
        TokenType.MULTIPLICACION,
        TokenType.DIVISION,
        TokenType.POTENCIA,
        TokenType.PAREN_ABRE,
    )


# ============================================================
# Tokeniza una línea usando el AFD
# ============================================================
def tokenizar_linea(linea: str, all_tokens: list) -> None:
    # Eliminar saltos de línea (Unix \n y Windows \r\n)
    s = linea.rstrip('\r\n')
    n = len(s)

    estado = Estado.q0
    lexema = ""
    i = 0

    def emitir(tipo: TokenType):
        nonlocal lexema, estado
        if lexema:
            all_tokens.append(Token(lexema, tipo))
            lexema = ""
        estado = Estado.q0

    def emitir_val(val: str, tipo: TokenType):
        all_tokens.append(Token(val, tipo))

    while i <= n:
        c = s[i] if i < n else '\0'  # '\0' = centinela fin de línea

        # Fin de línea: vaciar cualquier token en construcción
        if c == '\0':
            if estado == Estado.q1:
                emitir(TokenType.VARIABLE)
            elif estado == Estado.q2:
                emitir(TokenType.ENTERO)
            elif estado in (Estado.q3, Estado.q6):
                emitir(TokenType.REAL)
            elif estado in (Estado.q4, Estado.q5):
                emitir(TokenType.ERROR)   # E/e sin exponente
            elif lexema:
                emitir(TokenType.ERROR)
            break

        # ---- q0: ESTADO INICIAL --------------------------------
        if estado == Estado.q0:

            # Espacios en blanco
            if c in (' ', '\t'):
                i += 1
                continue

            # Comentario '//' — revisado antes que '/'
            if c == '/' and i + 1 < n and s[i + 1] == '/':
                emitir_val(s[i:], TokenType.COMENTARIO)
                i = n
                continue

            # Operadores y símbolos de un solo carácter
            single = {
                '=': TokenType.ASIGNACION,
                '+': TokenType.SUMA,
                '*': TokenType.MULTIPLICACION,
                '/': TokenType.DIVISION,
                '^': TokenType.POTENCIA,
                '(': TokenType.PAREN_ABRE,
                ')': TokenType.PAREN_CIERRA,
            }
            if c in single:
                emitir_val(c, single[c])
                i += 1
                continue

            # '-' : unario o binario
            if c == '-':
                nxt  = s[i + 1] if i + 1 < n else '\0'
                nxt2 = s[i + 2] if i + 2 < n else '\0'
                unario = es_contexto_unario(all_tokens)

                if unario and nxt.isdigit():
                    # Ej: -8  → número negativo entero/real
                    lexema = '-'
                    i += 1
                    estado = Estado.q2
                elif unario and nxt == '.' and nxt2.isdigit():
                    # Ej: -.5  → real negativo sin dígito antes del punto
                    lexema = '-.'
                    i += 2
                    estado = Estado.q3
                else:
                    emitir_val('-', TokenType.RESTA)
                    i += 1
                continue

            # Dígito → inicio de entero o real
            if c.isdigit():
                lexema += c
                i += 1
                estado = Estado.q2
                continue

            # Punto seguido de dígito → real sin dígito inicial (.5)
            if c == '.' and i + 1 < n and s[i + 1].isdigit():
                lexema = '.'
                i += 1
                estado = Estado.q3
                continue

            # Letra → inicio de identificador
            if c.isalpha():
                lexema += c
                i += 1
                estado = Estado.q1
                continue

            # Carácter desconocido
            emitir_val(c, TokenType.ERROR)
            i += 1

        # ---- q1: IDENTIFICADOR ---------------------------------
        elif estado == Estado.q1:
            if c.isalpha() or c.isdigit() or c == '_':
                lexema += c
                i += 1
            else:
                emitir(TokenType.VARIABLE)
                # NO incrementar i → el char se reprocesa en q0

        # ---- q2: ENTERO ----------------------------------------
        elif estado == Estado.q2:
            if c.isdigit():
                lexema += c
                i += 1
            elif c == '.':
                lexema += c
                i += 1
                estado = Estado.q3
            elif c in ('E', 'e'):
                lexema += c
                i += 1
                estado = Estado.q4
            else:
                emitir(TokenType.ENTERO)  # reprocesa c en q0

        # ---- q3: REAL (parte decimal) --------------------------
        elif estado == Estado.q3:
            if c.isdigit():
                lexema += c
                i += 1
            elif c in ('E', 'e'):
                lexema += c
                i += 1
                estado = Estado.q4
            else:
                emitir(TokenType.REAL)    # reprocesa c en q0

        # ---- q4: Después de E/e --------------------------------
        elif estado == Estado.q4:
            if c in ('+', '-'):
                lexema += c
                i += 1
                estado = Estado.q5
            elif c.isdigit():
                lexema += c
                i += 1
                estado = Estado.q6
            else:
                emitir(TokenType.ERROR)   # E/e sin signo ni dígito

        # ---- q5: Después de E+/E- ------------------------------
        elif estado == Estado.q5:
            if c.isdigit():
                lexema += c
                i += 1
                estado = Estado.q6
            else:
                emitir(TokenType.ERROR)

        # ---- q6: Dígitos del exponente -------------------------
        elif estado == Estado.q6:
            if c.isdigit():
                lexema += c
                i += 1
            else:
                emitir(TokenType.REAL)    # reprocesa c en q0

        else:
            i += 1


# ============================================================
# Función principal del lexer
# ============================================================
def lexer_aritmetico(archivo: str) -> None:
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            lineas = f.readlines()
    except FileNotFoundError:
        print(f"Error: no se pudo abrir el archivo '{archivo}'")
        return

    all_tokens = []

    for linea in lineas:
        tokenizar_linea(linea, all_tokens)

    # --- Impresión de la tabla de tokens ---
    W = 32
    print(f"{'Token':<{W}}{'Tipo'}")
    print('-' * (W + 28))

    for tok in all_tokens:
        print(f"{tok.valor:<{W}}{NOMBRE_TIPO[tok.tipo]}")


# ============================================================
# Entry point
# ============================================================
if __name__ == '__main__':
    if len(sys.argv) < 2:
        print(f"Uso: python {sys.argv[0]} <archivo.txt>")
        sys.exit(1)
    lexer_aritmetico(sys.argv[1])
