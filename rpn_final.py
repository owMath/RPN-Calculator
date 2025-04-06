"""
Calculadora RPN para Arduino - Implementação IEEE 754 Half Precision (16 bits)

Este programa lê expressões RPN de um arquivo de texto, calcula os resultados
e gera código Assembly correspondente para o microcontrolador ATmega328P.

Alunos: 
- Gabriel Martins Vicente
- Javier Agustin Aranibar González
- Matheus Paul Lopuch
- Rafael Bonfim Zacco

Grupo 04
"""
import sys  # Para acessar argumentos da linha de comando
import re   # Para usar expressões regulares
import math # Para operações matemáticas

def float_to_half_ieee754(f):
    """
    Converte um número float para formato IEEE 754 half-precision (16 bits)
    
    Formato IEEE 754 half-precision:
    1 bit: Sinal
    5 bits: Expoente (bias de 15)
    10 bits: Mantissa (parte fracionária)
    
    Args:
        f (float): Valor float a ser convertido
        
    Returns:
        int: Representação de 16 bits em formato IEEE 754 half-precision
    """
    # Tratamento de casos especiais
    if f == 0.0: return 0x0000  # Zero positivo
    if f < 0.0 and f == 0.0: return 0x8000  # Zero negativo
    if f == float('inf'): return 0x7C00  # Infinito positivo
    if f == float('-inf'): return 0xFC00  # Infinito negativo
    if math.isnan(f): return 0x7E00  # NaN (Not a Number)
    
    # Extrair sinal, expoente e mantissa
    sinal = 0x8000 if f < 0 else 0
    f = abs(f)
    
    # Normalizar para o formato IEEE 754
    if f >= 2.0 ** (-14):  # Valores normalizados
        expoente = math.floor(math.log2(f))
        mantissa = f / (2 ** expoente) - 1.0
        expoente_ajustado = expoente + 15  # Bias de 15
        
        # Verificar limites
        if expoente_ajustado < 0: return sinal  # Underflow
        if expoente_ajustado > 31: return sinal | 0x7C00  # Overflow
        
        # Calcular os bits da mantissa (10 bits)
        bits_mantissa = int(mantissa * 1024 + 0.5)
        half = sinal | ((expoente_ajustado & 0x1F) << 10) | (bits_mantissa & 0x3FF)
    else:  # Valores desnormalizados
        mantissa = f / (2 ** (-14))
        bits_mantissa = int(mantissa * 1024 + 0.5)
        half = sinal | (bits_mantissa & 0x3FF)
    
    return half

def half_ieee754_to_float(h):
    """
    Converte um número IEEE 754 half-precision (16 bits) para float
    
    Args:
        h (int): Valor de 16 bits em formato IEEE 754 half-precision
        
    Returns:
        float: Valor float correspondente
    """
    # Extrair componentes
    sinal = -1.0 if (h & 0x8000) else 1.0
    expoente = (h >> 10) & 0x1F
    mantissa = h & 0x3FF
    
    # Casos especiais
    if expoente == 0:
        if mantissa == 0: return 0.0 * sinal  # Zero com sinal
        # Número desnormalizado
        return sinal * (mantissa / 1024.0) * (2 ** -14)
    elif expoente == 31:
        if mantissa == 0: return float('inf') * sinal  # Infinito com sinal
        return float('nan')  # NaN
    
    # Número normalizado
    return sinal * (1.0 + mantissa / 1024.0) * (2 ** (expoente - 15))

def add_half_precision(a, b):
    """
    Soma dois números em formato IEEE 754 half-precision
    
    Args:
        a (int): Primeiro operando em formato half-precision
        b (int): Segundo operando em formato half-precision
        
    Returns:
        int: Resultado da soma em formato half-precision
    """
    fa, fb = half_ieee754_to_float(a), half_ieee754_to_float(b)
    return float_to_half_ieee754(fa + fb)

def sub_half_precision(a, b):
    """
    Subtração de dois números em formato IEEE 754 half-precision
    
    Args:
        a (int): Primeiro operando em formato half-precision
        b (int): Segundo operando em formato half-precision
        
    Returns:
        int: Resultado da subtração em formato half-precision
    """
    fa, fb = half_ieee754_to_float(a), half_ieee754_to_float(b)
    return float_to_half_ieee754(fa - fb)

def mul_half_precision(a, b):
    """
    Multiplicação de dois números em formato IEEE 754 half-precision
    
    Args:
        a (int): Primeiro operando em formato half-precision
        b (int): Segundo operando em formato half-precision
        
    Returns:
        int: Resultado da multiplicação em formato half-precision
    """
    fa, fb = half_ieee754_to_float(a), half_ieee754_to_float(b)
    return float_to_half_ieee754(fa * fb)

def div_half_precision(a, b):
    """
    Divisão de dois números em formato IEEE 754 half-precision
    
    Args:
        a (int): Primeiro operando em formato half-precision
        b (int): Segundo operando em formato half-precision
        
    Returns:
        int: Resultado da divisão em formato half-precision
    """
    fa, fb = half_ieee754_to_float(a), half_ieee754_to_float(b)
    # Verificar divisão por zero
    if fb == 0: return 0x7C00 if fa >= 0 else 0xFC00  # Infinito com sinal (divisão por 0)
    return float_to_half_ieee754(fa / fb)

def power_half_precision(a, b):
    """
    Potenciação em formato IEEE 754 half-precision
    
    Args:
        a (int): Base em formato half-precision
        b (int): Expoente em formato half-precision
        
    Returns:
        int: Resultado da potenciação em formato half-precision
    """
    fa, fb = half_ieee754_to_float(a), half_ieee754_to_float(b)
    try:
        return float_to_half_ieee754(fa ** fb)
    except:
        return 0x7E00  # NaN para casos de erro

def mod_half_precision(a, b):
    """
    Operação de módulo em formato IEEE 754 half-precision
    
    Args:
        a (int): Primeiro operando em formato half-precision
        b (int): Segundo operando em formato half-precision
        
    Returns:
        int: Resultado do módulo em formato half-precision
    """
    fa, fb = half_ieee754_to_float(a), half_ieee754_to_float(b)
    # Verificar divisão por zero
    if fb == 0: return 0x7E00  # NaN
    return float_to_half_ieee754(fa % fb)

def read_expressions_file(filename):
    """
    Lê expressões RPN de um arquivo de texto.
    
    Args:
        filename (str): Nome do arquivo a ser lido
        
    Returns:
        list: Lista de expressões lidas do arquivo
        
    Raises:
        SystemExit: Se o arquivo não for encontrado
    """
    try:
        with open(filename, 'r') as file:
            return [line.strip() for line in file if line.strip()]
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado.")
        sys.exit(1)  # Encerra o programa com código de erro

def resolve(expressao, memoria, ultimo_resultado, file, k):
    """
    Resolve uma expressão RPN e escreve o código assembly correspondente
    
    Args:
        expressao (str): Expressão RPN a ser resolvida
        memoria (float): Valor atual armazenado na memória
        ultimo_resultado (float): Último resultado calculado
        file (file): Arquivo de saída para código assembly
        k (list): Contador para rótulos únicos
        
    Returns:
        float: Resultado da expressão calculada
    """
    # Verificar e tratar caso especial (MEM RES) sem operador
    if re.search(r'\(\s*MEM\s+RES\s*\)', expressao):
        expressao = expressao.replace('(MEM RES)', f'(MEM RES +)')
    
    # Substituir vírgulas por pontos (para números decimais)
    expressao = expressao.replace(',', '.')
    
    # Substituir MEM pelo valor armazenado na memória
    expressao = re.sub(r'\bMEM\b', str(memoria), expressao)
    
    # Substituir RES pelo último resultado calculado
    expressao = re.sub(r'\bRES\b', str(ultimo_resultado), expressao)
    
    # Extrair elementos da expressão
    elementos = re.findall(r'-?[\d.]+|[()+\-*^/%|]', expressao)
    
    # Processar a expressão
    pilha = []
    for elemento in elementos:
        # Números: empilhar diretamente
        if elemento.isdigit() or re.match(r'-?\d*\.\d+', elemento) or re.match(r'-?\d+', elemento):
            pilha.append(float(elemento))
        # Parêntese de abertura: empilhar diretamente
        elif elemento == '(':
            pilha.append('(')
        # Parêntese de fechamento: processar subexpressão
        elif elemento == ')':
            subexpressao = []
            # Desempilhar até encontrar o parêntese correspondente
            while pilha and pilha[-1] != '(':
                subexpressao.insert(0, pilha.pop())
            # Verificar parênteses desbalanceados
            if not pilha:
                print("Erro: Parênteses desbalanceados")
                return None
            # Remover o parêntese de abertura
            pilha.pop()
            # Incrementar k para rótulos únicos
            k[0] += 1
            # Resolver a subexpressão
            resultado_subexpressao = resolve_subexpressao_ieee754(subexpressao, file, k, memoria)
            # Verificar erro na subexpressão
            if resultado_subexpressao is None: return None
            # Empilhar o resultado
            pilha.append(resultado_subexpressao)
        # Operadores e outros: empilhar diretamente (serão processados depois)
        else:
            pilha.append(elemento)
    
    # Incrementar k para rótulos únicos
    k[0] += 1
    # Processar a pilha final
    resultado_final = resolve_subexpressao_ieee754(pilha, file, k, memoria)
    # Verificar erro no processamento
    if resultado_final is None: return None
    
    # Formatar resultado para output
    if isinstance(resultado_final, float) and resultado_final.is_integer():
        resultado_str = str(int(resultado_final))
    else:
        resultado_str = f"{resultado_final:.1f}".rstrip('0').rstrip('.')
    
    # Escrever código para enviar o resultado
    file.write("""
    ; Enviar resultado
    LDI R16, '='
    RCALL uart_envia_byte
    LDI R16, ' '
    RCALL uart_envia_byte
    """)
    
    # Enviar cada dígito do resultado
    for char in resultado_str:
        file.write(f"""
    LDI R16, '{char}'
    RCALL uart_envia_byte
    """)
    
    # Enviar nova linha e delay
    file.write(f"""
    ; Enviar nova linha
    LDI R16, 13  ; CR
    RCALL uart_envia_byte
    LDI R16, 10  ; LF
    RCALL uart_envia_byte
    
    ; Delay para visualização
    RCALL delay_ms
""")
    return resultado_final

def resolve_subexpressao_ieee754(subexpressao, file, k, memoria):
    """
    Resolve uma subexpressão usando IEEE 754 half-precision e escreve o código assembly correspondente
    
    Args:
        subexpressao (list): Lista de elementos da subexpressão
        file (file): Arquivo de saída para código assembly
        k (list): Contador para rótulos únicos
        memoria (float): Valor atual armazenado na memória
        
    Returns:
        float: Resultado da subexpressão calculada
    """
    pilha = []
    for elemento in subexpressao:
        # Verificar se é um operador
        if elemento in {'+', '-', '*', '|', '/', '^', '%'}:
            # Verificar se há operandos suficientes
            if len(pilha) < 2:
                print(f"Erro: Número insuficiente de operandos para o operador {elemento}")
                return None
            # Obter os operandos
            operando2 = pilha.pop()
            operando1 = pilha.pop()
            
            # Divisão inteira (operador /)
            if elemento == '/': 
                # Verificar divisão por zero
                if operando2 == 0:
                    print(f"Erro: Divisão por zero ({operando1} / {operando2})")
                    return None
                # Converter para inteiros
                operando1_int = int(float(operando1))
                operando2_int = int(float(operando2))
                # Calcular resultado
                resultado = operando1_int // operando2_int
                pilha.append(float(resultado))
                
                # Gerar código Assembly para divisão inteira
                file.write(f"""
    ; {operando1} / {operando2} (Divisão inteira)
    LDI R16, {operando1_int & 0xFF}
    LDI R17, {(operando1_int >> 8) & 0xFF}
    LDI R18, {operando2_int & 0xFF}
    LDI R19, {(operando2_int >> 8) & 0xFF}
    RCALL integer_divide
""")
            # Outros operadores (half-precision)
            else:
                # Converter para formato half-precision
                operando1_half = float_to_half_ieee754(float(operando1))
                operando2_half = float_to_half_ieee754(float(operando2))
                
                # Mapeamento de operadores para funções e comandos assembly
                op_map = {
                    '+': (add_half_precision, 'half_add'),
                    '-': (sub_half_precision, 'half_subtract'),
                    '*': (mul_half_precision, 'half_multiply'),
                    '|': (div_half_precision, 'half_divide'),
                    '^': (power_half_precision, 'half_power'),
                    '%': (mod_half_precision, 'half_modulo')
                }
                
                # Obter a função e o comando assembly correspondentes
                func, asm_cmd = op_map[elemento]
                
                # Gerar código Assembly para a operação
                file.write(f"""
    ; {operando1} {elemento} {operando2} (IEEE 754 half-precision)
    LDI R16, {operando1_half & 0xFF}
    LDI R17, {(operando1_half >> 8) & 0xFF}
    LDI R18, {operando2_half & 0xFF}
    LDI R19, {(operando2_half >> 8) & 0xFF}
    RCALL {asm_cmd}
""")
                # Calcular resultado
                resultado_half = func(operando1_half, operando2_half)
                resultado = half_ieee754_to_float(resultado_half)
                pilha.append(resultado)
        # Se não for um operador, empilhar como número
        else:
            pilha.append(float(elemento))
    
    # Verificar se a expressão é válida (deve ter exatamente um resultado na pilha)
    if len(pilha) != 1:
        print(f"Erro: Subexpressão inválida, pilha final: {pilha}")
        return None
    return pilha[0]

def adicionar_rotinas_ieee754(file):
    """
    Adiciona as rotinas de manipulação IEEE 754 ao arquivo Assembly
    
    Args:
        file (file): Arquivo de saída para código assembly
    """
    file.write("""
;***********************************************************************************************
; Rotinas para manipulação de números IEEE 754 half-precision (16 bits)
;***********************************************************************************************

half_add:
    ; Empilhar registradores
    PUSH R20
    PUSH R21
    PUSH R22
    PUSH R23
    PUSH R24
    PUSH R25

    ; Extrair componentes do primeiro operando (a)
    MOV R20, R17         ; r20 = byte alto de a
    ANDI R20, 0x80       ; r20 = bit de sinal de a
    MOV R21, R17
    ANDI R21, 0x7C       ; r21 = 5 bits de expoente (parte alta) / bit de sinal (bit 8) e ignorando mantissa
    LSR R21
    LSR R21              ; r21 = expoente >> 2 / R21 > menos significativo a mantissa (2 zeros a esquerda)
    MOV R22, R17         ; começo da extração da mantissa
    ANDI R22, 0x03       ; r22 = 2 bits mais altos da mantissa
    LSL R22
    LSL R22
    LSL R22
    LSL R22
    LSL R22
    LSL R22              ; r22 = bits altos da mantissa deslocados
    OR R22, R16          ; r22:r16 = mantissa completa

    ; Extrair componentes do segundo operando (b)
    MOV R23, R19         ; r23 = byte alto de b
    ANDI R23, 0x80       ; r23 = bit de sinal de b
    MOV R24, r19
    ANDI R24, 0x7C       ; r24 = 5 bits de expoente (parte alta)
    LSR R24
    LSR R24              ; r24 = expoente >> 2
    MOV R25, R19
    ANDI R25, 0x03       ; r25 = 2 bits mais altos da mantissa
    LSL R25
    LSL R25
    LSL R25
    LSL R25
    LSL R25
    LSL R25              ; r25 = bits altos da mantissa deslocados
    OR R25, R18          ; r25:r18 = mantissa completa

    ; Alinhar expoentes
    CP R21, R24
    BREQ exponents_equal
    BRLO a_smaller
    
    ; Expoente de a é maior
    SUB R21, R24         ; Diferença entre expoentes
    ; Ajustar mantissa de b
    LSR R25
    JMP exponents_equal
    
a_smaller:
    ; Expoente de b é maior
    SUB R24, R21         ; Diferença entre expoentes
    ; Ajustar mantissa de a
    LSR R22
    
exponents_equal:
    ; Verificar sinais para soma/subtração
    CP R20, R23
    BREQ same_sign
    
    ; Sinais diferentes - realizar subtração
    JMP result_ready
    
same_sign:
    ; Sinais iguais - realizar soma
    ADD R16, R18         ; Somar bytes baixos da mantissa
    ADC R22, R25         ; Somar bytes altos da mantissa com carry
    
result_ready:
    ; Reconstruir o número IEEE 754 de 16 bits
    MOV R17, R20         ; Colocar bit de sinal
    
    ; Restaurar registradores
    POP R25
    POP R24
    POP R23
    POP R22
    POP R21
    POP R20
    RET

half_subtract:
    ; Empilhar registradores
    PUSH R20
    PUSH R21
    PUSH R22
    PUSH R23
    PUSH R24
    PUSH R25

    ; Extrair componentes do primeiro operando (a)
    MOV R20, R17         ; r20 = byte alto de a
    ANDI R20, 0x80       ; r20 = bit de sinal de a
    MOV R21, R17
    ANDI R21, 0x7C       ; r21 = 5 bits de expoente (parte alta)
    LSR R21
    LSR R21              ; r21 = expoente >> 2
    MOV R22, R17
    ANDI R22, 0x03       ; r22 = 2 bits mais altos da mantissa
    LSL R22
    LSL R22
    LSL R22
    LSL R22
    LSL R22
    LSL R22              ; r22 = bits altos da mantissa deslocados
    OR R22, R16          ; r22:r16 = mantissa completa

    ; Extrair componentes do segundo operando (b)
    MOV R23, R19         ; r23 = byte alto de b
    ANDI R23, 0x80       ; r23 = bit de sinal de b
    MOV R24, R19
    ANDI R24, 0x7C       ; r24 = 5 bits de expoente (parte alta)
    LSR R24
    LSR R24              ; r24 = expoente >> 2
    MOV R25, R19
    ANDI R25, 0x03       ; r25 = 2 bits mais altos da mantissa
    LSL R25
    LSL R25
    LSL R25
    LSL R25
    LSL R25
    LSL R25              ; r25 = bits altos da mantissa deslocados
    OR R25, R18          ; r25:r18 = mantissa completa

    ; Inverter o sinal do segundo operando (transformar subtração em adição com sinal invertido)
    LDI R19, 0x80
    EOR R23, R19         ; Inverte o bit de sinal de b
    
    ; Alinhar expoentes
    CP R21, R24
    BREQ sub_exponents_equal
    BRLO sub_a_smaller
    
    ; Expoente de a é maior
    SUB R21, R24         ; Diferença entre expoentes
    ; Ajustar mantissa de b
    LSR R25
    DEC R21
    BRNE sub_exponents_equal
    JMP sub_exponents_equal
    
sub_a_smaller:
    ; Expoente de b é maior
    SUB R24, R21         ; Diferença entre expoentes
    ; Ajustar mantissa de a
    LSR R22
    DEC R24
    BRNE sub_a_smaller
    
sub_exponents_equal:
    ; Verificar sinais para soma/subtração
    CP R20, R23
    BREQ sub_same_sign
    
    ; Sinais diferentes - realizar subtração
    SUB R16, R18         ; Subtrair bytes baixos da mantissa
    SBC R22, R25         ; Subtrair bytes altos da mantissa com carry
    JMP sub_result_ready
    
sub_same_sign:
    ; Sinais iguais - realizar soma
    ADD R16, R18         ; Somar bytes baixos da mantissa
    ADC R22, R25         ; Somar bytes altos da mantissa com carry
    
sub_result_ready:
    ; Reconstruir o número IEEE 754 de 16 bits
    MOV R17, R20         ; Colocar bit de sinal
    
    ; Normalizar resultado se necessário
    SBRC R22, 7          ; Se bit 7 estiver setado, ajustar expoente
    INC R21              ; Incrementar expoente
    
    ; Inserir expoente
    LSL R21
    LSL R21              ; Deslocar expoente
    ANDI R17, 0x83       ; Manter sinal e 2 bits altos da mantissa
    ANDI R21, 0x7C       ; Manter apenas os 5 bits do expoente
    OR R17, R21          ; Combinar sinal + expoente + bits altos da mantissa
    
    ; Restaurar registradores
    POP R25
    POP R24
    POP R23
    POP R22
    POP R21
    POP R20
    RET

half_multiply:
    ; Empilhar registradores
    PUSH R20
    PUSH R21
    PUSH R22
    PUSH R23
    PUSH R24
    PUSH R25
    
    ; Extrair sinal (XOR dos bits de sinal)
    MOV R20, R17         ; Byte alto de a
    ANDI R20, 0x80       ; Bit de sinal de a
    MOV R21, R19         ; Byte alto de b
    ANDI R21, 0x80       ; Bit de sinal de b
    EOR R20, R21         ; r20 = sinal do resultado
    
    ; Extrair expoentes
    MOV R21, R17
    ANDI R21, 0x7C       ; 5 bits de expoente de a
    LSR R21
    LSR R21              ; r21 = expoente normalizado
    
    MOV R22, R19
    ANDI R22, 0x7C       ; 5 bits de expoente de b
    LSR R22
    LSR R22              ; r22 = expoente normalizado
    
    ; Somar expoentes e subtrair bias (15)
    ADD R21, R22
    SUBI R21, 15         ; r21 = expoente final
    
    ; Reconstruir o número IEEE 754 de 16 bits
    MOV R17, R20         ; Colocar bit de sinal
    
    ; Restaurar registradores
    POP R25
    POP R24
    POP R23
    POP R22
    POP R21
    POP R20
    RET

half_divide:
    ; Empilhar registradores
    PUSH R20
    PUSH R21
    PUSH R22
    PUSH R23
    PUSH R24
    PUSH R25
    
    ; Verificar divisão por zero
    MOV R20, R18
    OR R20, R19
    BREQ half_div_by_zero
    
    ; Extrair sinal (XOR dos bits de sinal)
    MOV R20, R17         ; Byte alto de a
    ANDI R20, 0x80       ; Bit de sinal de a
    MOV R21, R19         ; Byte alto de b
    ANDI R21, 0x80       ; Bit de sinal de b
    EOR R20, R21         ; r20 = sinal do resultado
    
    ; Extrair expoentes
    MOV R21, R17
    ANDI R21, 0x7C       ; 5 bits de expoente de a
    LSR R21
    LSR R21              ; r21 = expoente normalizado
    
    MOV R22, R19
    ANDI R22, 0x7C       ; 5 bits de expoente de b
    LSR R22
    LSR R22              ; r22 = expoente normalizado
    
    ; Calcular expoente do resultado: exp_a - exp_b + bias(15)
    SUB R21, R22
    SUBI R21, -15        ; Adicionar bias (usando subtração negativa)
    
    ; Extrair mantissas
    MOV R22, R17
    ANDI R22, 0x03       ; 2 bits mais altos da mantissa de a
    LSL R22
    LSL R22
    LSL R22
    LSL R22
    LSL R22
    LSL R22              ; r22 = bits altos da mantissa deslocados
    OR R22, R16          ; r22:r16 = mantissa completa de a
    
    MOV R23, R19
    ANDI R23, 0x03       ; 2 bits mais altos da mantissa de b
    LSL R23
    LSL R23
    LSL R23
    LSL R23
    LSL R23
    LSL R23              ; r23 = bits altos da mantissa deslocados
    OR R23, R18          ; r23:r18 = mantissa completa de b
    
    ; Adicionar bit implícito para mantissas normalizadas
    ORI R22, 0x40        ; Adicionar bit implícito à mantissa de a
    ORI R23, 0x40        ; Adicionar bit implícito à mantissa de b
    
    ; Realizar a divisão da mantissa (simplificada)
    ; Normalmente, isso seria feito com uma rotina de divisão completa
    ; Mas para simplificar, assumimos que a mantissa do resultado é aproximada
    
    ; Reconstruir o número IEEE 754 de 16 bits
    MOV R17, R20         ; Colocar bit de sinal
    
    ; Inserir expoente
    LSL R21
    LSL R21              ; Deslocar expoente
    ANDI R17, 0x83       ; Manter sinal e 2 bits altos da mantissa
    ANDI R21, 0x7C       ; Manter apenas os 5 bits do expoente
    OR R17, R21          ; Combinar sinal + expoente + bits altos da mantissa
    
    ; Restaurar registradores
    POP R25
    POP R24
    POP R23
    POP R22
    POP R21
    POP R20
    RET
    
half_div_by_zero:
    ; Extrair o sinal do numerador (a)
    MOV R20, R17
    ANDI R20, 0x80       ; Bit de sinal de a
    
    ; Gerar infinito com o sinal apropriado
    LDI R16, 0x00        ; Byte baixo para infinito
    LDI R17, 0x7C        ; Byte alto para infinito positivo
    OR R17, R20          ; Aplicar sinal ao infinito
    
    ; Restaurar registradores
    POP R25
    POP R24
    POP R23
    POP R22
    POP R21
    POP R20
    RET

half_power:
    ; Empilhar registradores
    PUSH R20
    PUSH R21
    PUSH R22
    PUSH R23
    PUSH R24
    PUSH R25
    
    ; Verificar casos especiais
    ; Caso 1: Se expoente for 0, retornar 1.0
    MOV R20, R18
    OR R20, R19
    BREQ power_one       ; Se expoente for zero, resultado é 1.0
    
    ; Caso 2: Se base for 1.0, retornar 1.0
    LDI R20, 0x00
    CP R16, R20
    BRNE check_base_neg
    LDI R20, 0x3C        ; 1.0 em half-precision
    CP R17, R20
    BREQ power_one       ; Se base for 1.0, resultado é 1.0
    
check_base_neg:
    ; Caso 3: Se base for negativa, verificar se expoente é inteiro
    MOV R20, R17
    ANDI R20, 0x80
    BREQ base_positive   ; Se base for positiva, prosseguir normalmente
    
    ; Base é negativa, verificar se expoente é inteiro
    ; Para simplificar, vamos retornar NaN para base negativa
    JMP power_nan
    
base_positive:
    ; Implementação simplificada: para potência, usamos logaritmo
    ; ln(a^b) = b * ln(a), depois exp()
    ; Como isso requer funções transcendentais complexas,
    ; vamos implementar apenas casos especiais comuns
    
    ; Caso especial: Se expoente for 0.5, calcular raiz quadrada
    LDI R20, 0x00
    CP R18, R20
    BRNE power_approx
    LDI R20, 0x38        ; 0.5 em half-precision
    CP R19, R20
    BRNE power_approx
    
    ; Calcular raiz quadrada (aproximação)
    ; Para simplificar, dividimos o expoente por 2
    MOV R21, R17
    ANDI R21, 0x7C       ; Expoente da base
    LSR R21              ; Dividir expoente por 2
    ANDI R17, 0x83       ; Manter sinal e parte da mantissa
    OR R17, R21          ; Recombinar
    JMP power_done
    
power_approx:
    ; Implementação muito simplificada para outros casos
    ; Ajuste de expoente aproximado para operações de potência
    ; Em uma implementação real, um algoritmo mais complexo seria necessário
    
power_done:
    ; Restaurar registradores
    POP R25
    POP R24
    POP R23
    POP R22
    POP R21
    POP R20
    RET
    
power_one:
    ; Retornar 1.0
    LDI R16, 0x00
    LDI R17, 0x3C        ; 1.0 em half-precision
    
    ; Restaurar registradores
    POP R25
    POP R24
    POP R23
    POP R22
    POP R21
    POP R20
    RET
    
power_nan:
    ; Retornar NaN
    LDI R16, 0x00
    LDI R17, 0x7E        ; NaN em half-precision
    
    ; Restaurar registradores
    POP R25
    POP R24
    POP R23
    POP R22
    POP R21
    POP R20
    RET

half_modulo:
    ; Empilhar registradores
    PUSH R20
    PUSH R21
    PUSH R22
    PUSH R23
    PUSH R24
    PUSH R25
    
    ; Verificar divisão por zero
    MOV R20, R18
    OR R20, R19
    BREQ mod_by_zero
    
    ; Extrair componentes do primeiro operando (a)
    MOV R20, R17         ; r20 = byte alto de a
    ANDI R20, 0x80       ; r20 = bit de sinal de a
    
    ; Extrair expoentes
    MOV R21, R17
    ANDI R21, 0x7C       ; 5 bits de expoente de a
    MOV R22, R19
    ANDI R22, 0x7C       ; 5 bits de expoente de b
    
    ; Verificar se b é maior que a
    CP R21, R22
    BRLO mod_a_smaller   ; Se expoente de a for menor, resultado é a
    
    ; Implementação simplificada de módulo
    ; Em uma implementação real, precisaríamos realizar a divisão,
    ; truncar para obter o quociente, multiplicar pelo divisor,
    ; e subtrair do dividendo
    
    ; Para simplificar, vamos retornar um valor aproximado baseado
    ; na comparação dos expoentes
    
mod_a_smaller:
    ; Se a < b, resultado do módulo é a
    MOV R16, R16
    MOV R17, R17
    JMP mod_done
    
mod_done:
    ; Restaurar registradores
    POP R25
    POP R24
    POP R23
    POP R22
    POP R21
    POP R20
    RET
    
mod_by_zero:
    ; Retornar NaN
    LDI R16, 0x00
    LDI R17, 0x7E        ; NaN em half-precision
    
    ; Restaurar registradores
    POP R25
    POP R24
    POP R23
    POP R22
    POP R21
    POP R20
    RET

integer_divide:
    ; Empilhar registradores
    PUSH R20
    PUSH R21
    PUSH R22
    PUSH R23
    
    ; Verificar divisão por zero
    MOV R20, R18
    OR R20, R19
    BREQ div_by_zero
    
    ; Salvar sinal
    MOV R20, R16
    EOR R20, R18         ; XOR para determinar o sinal do resultado
    ANDI R20, 0x80       ; Apenas o bit de sinal
    
    ; Resultado da divisão inteira em r16:r17
    ; Restaurar o sinal em r17
    ANDI R17, 0x7F       ; Limpar bit de sinal
    OR R17, r20          ; Aplicar bit de sinal
    
    ; Restaurar registradores
    POP R23
    POP R22
    POP R21
    POP R20
    RET
    
div_by_zero:
    ; Tratar divisão por zero
    LDI R16, 0xFF       ; Indicar erro
    LDI R17, 0xFF
    
    ; Restaurar registradores
    POP R23
    POP R22
    POP R21
    POP R20
    RET

;***********************************************************************************************

; Função para enviar um byte pela UART
uart_envia_byte:
    LDS R17, UCSR0A
    SBRS R17, 5
    RJMP uart_envia_byte
    STS UDR0, R16
    RET

; Função de delay em milissegundos
delay_ms:
    PUSH R20
    PUSH R21
    LDI R20, 100
delay_ms_outer:
    LDI R21, 255
delay_ms_inner:
    DEC R21
    BRNE delay_ms_inner
    DEC R20
    BRNE delay_ms_outer
    POP R21
    POP R20
    RET
""")

def main():
    """
    Função principal que orquestra o fluxo do programa:
    1. Lê o arquivo de entrada com expressões RPN
    2. Gera código Assembly para Arduino
    3. Exibe resultados e salva código Assembly em arquivo
    """
    # Verificar se o nome do arquivo foi fornecido
    if len(sys.argv) != 2:
        print("Uso: python rpn_calculator.py <arquivo>")
        sys.exit(1)
    
    # Ler as expressões do arquivo
    nomeArquivo = sys.argv[1].lower()
    linhas = read_expressions_file(nomeArquivo)

    # Criar arquivo de código Assembly
    with open('calculadora.asm', 'w') as file:
        # Escrever cabeçalho e configuração inicial
        file.write("""; Calculadora RPN - Código Assembly para ATmega328P (IEEE 754 Half-precision 16 bits)
; Alunos: Gabriel Martins Vicente, Javier Agustin Aranibar González, Matheus Paul Lopuch, Rafael Bonfim Zacco
;***********************************************************************************************
.equ SPH, 0x3E    ; Stack Pointer High
.equ SPL, 0x3D    ; Stack Pointer Low
.equ UBRR0L, 0xC4 ; Baud Rate Register Low
.equ UBRR0H, 0xC5 ; Baud Rate Regis ter High
; 3 registradores (UCSR0A, UCSR0B e UCSR0C) são todos necessários para configurar e controlar a UART corretamente
.equ UCSR0A, 0xC0 ; Control and Status Register A: Usado para verificar o status da UART, como a verificação de transmissão completa ou erro de paridade (bit 5: UDRE0)
.equ UCSR0B, 0xC1 ; Control and Status Register B: Responsável pelo controle da habilitação da UART, como o habilitamento de transmissor (bit TXEN0)
.equ UCSR0C, 0xC2 ; Control and Status Register C: Configurar o formato de dados da UART, como o número de bits por caractere, paridade e bits de stop
.equ UDR0, 0xC6   ; Registrador de dados para a UART0 (1° porta UART do microcontrolador), é utilizado para enviar e receber dados através da comunicação serial (buffer)
; Fórmula para definir o Universal Boud Rate Register (UBRR): UBRR = Fcpu / (16 * Baud Rate) -1
; Para o ATmega328P seria: 16MHz / (16 * 9600) - 1 = 103
;***********************************************************************************************

.ORG 0x0000
    RJMP reset
    
reset:
    ; Configurar stack pointer
    LDI R16, 0x08
    OUT SPH, r16
    LDI r16, 0xFF
    OUT SPL, r16
        
        ; Configurar UART
        LDI R16, 103
        STS UBRR0L, r16
        LDI R16, 0
        STS UBRR0H, r16
        LDI R16, 8
        STS UCSR0B, r16
        LDI R16, 6
        STS UCSR0C, r16
        
        ; Delay inicial
        LDI R20, 255
    delay_init_loop: ; Delay para estabilizar
    DEC R20
    BRNE delay_init_loop
    
    ; Enviar mensagem inicial
    LDI R16, 'C'
    RCALL uart_envia_byte
    LDI R16, 'a'
    RCALL uart_envia_byte
    LDI R16, 'l'
    RCALL uart_envia_byte
    LDI R16, 'c'
    RCALL uart_envia_byte
    LDI R16, 'u'
    RCALL uart_envia_byte
    LDI R16, 'l'
    RCALL uart_envia_byte
    LDI R16, 'a'
    RCALL uart_envia_byte
    LDI R16, 'd'
    RCALL uart_envia_byte
    LDI R16, 'o'
    RCALL uart_envia_byte
    LDI R16, 'r'
    RCALL uart_envia_byte
    LDI R16, 'a'
    RCALL uart_envia_byte
    LDI R16, ' '
    RCALL uart_envia_byte
    LDI R16, 'R'
    RCALL uart_envia_byte
    LDI R16, 'P'
    RCALL uart_envia_byte
    LDI R16, 'N'
    RCALL uart_envia_byte
    LDI R16, ':'
    RCALL uart_envia_byte
    LDI R16, 13
    RCALL uart_envia_byte
    LDI R16, 10
    RCALL uart_envia_byte
    LDI R16, 13
    RCALL uart_envia_byte
    LDI R16, 10
    RCALL uart_envia_byte
    
main:
""")
        
        # Inicializar variáveis de estado
        memoria = 0
        ultimo_resultado = 0
        k = [0]  # Contador para rótulos únicos (usando lista para ser modificável nas funções)
        resultados = []
        
        # Processar cada expressão
        for i, expressao in enumerate(linhas):
            expressao_original = expressao
            expressao_calculo = expressao
            
            # Processar referências a resultados anteriores (n RES)
            match_res = re.search(r'\(\s*(\d+)\s+RES\s*\)', expressao_calculo)
            if match_res:
                n = int(match_res.group(1))
                indice_anterior = i - n
                if 0 <= indice_anterior < len(resultados):
                    valor_anterior = resultados[indice_anterior]
                    expressao_calculo = f"({valor_anterior})"
                else:
                    print(f"Erro: Referência inválida - linha {indice_anterior+1} não existe")
                    continue
            
            # Processar armazenamento em memória (n MEM)
            match_mem = re.search(r'\(\s*(\d+\.?\d*)\s+MEM\s*\)', expressao_calculo)
            if match_mem:
                memoria = float(match_mem.group(1))
                expressao_calculo = f"({memoria})"
            
            # Escrever código para enviar a expressão original
            file.write(f"\n    ; Calculando: {expressao_original}\n")
            
            # Enviar cada caractere da expressão original
            for char in expressao_original:
                if char in "()+-*/^%|" or char.isdigit() or char == '.' or char == ' ' or char in "RESM":
                    file.write(f"""
    LDI R16, '{char}'
    RCALL uart_envia_byte
""")

            # Resolver a expressão e gerar código assembly
            resultado = resolve(expressao_calculo, memoria, ultimo_resultado, file, k)
            if resultado is None:
                print(f"Erro ao processar a expressão {expressao_original}")
                continue
                
            # Armazenar resultado para uso posterior
            resultados.append(resultado)
            ultimo_resultado = resultado
        
        # Adicionar rotinas utilitárias
        file.write("""
    ; Loop infinito
loop_end:
    RJMP loop_end
""")
        # Adicionar rotinas para operações IEEE 754 half-precision
        adicionar_rotinas_ieee754(file)
    
    print("Arquivo Calculadora.asm gerado com sucesso!")

if __name__ == "__main__":
    main()
    
