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
    if fb == 0: return 0x7C00 if fa >= 0 else 0xFC00  # Infinito com sinal
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
    ldi r16, '='
    rcall uart_envia_byte
    ldi r16, ' '
    rcall uart_envia_byte
    """)
    
    # Enviar cada dígito do resultado
    for char in resultado_str:
        file.write(f"""
    ldi r16, '{char}'
    rcall uart_envia_byte
    """)
    
    # Enviar nova linha e delay
    file.write(f"""
    ; Enviar nova linha
    ldi r16, 13  ; CR
    rcall uart_envia_byte
    ldi r16, 10  ; LF
    rcall uart_envia_byte
    
    ; Delay para visualização
    rcall delay_ms
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
    ldi r16, {operando1_int & 0xFF}
    ldi r17, {(operando1_int >> 8) & 0xFF}
    ldi r18, {operando2_int & 0xFF}
    ldi r19, {(operando2_int >> 8) & 0xFF}
    rcall integer_divide
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
    ldi r16, {operando1_half & 0xFF}
    ldi r17, {(operando1_half >> 8) & 0xFF}
    ldi r18, {operando2_half & 0xFF}
    ldi r19, {(operando2_half >> 8) & 0xFF}
    rcall {asm_cmd}
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
    push r20
    push r21
    push r22
    push r23
    push r24
    push r25

    ; Extrair componentes do primeiro operando (a)
    mov r20, r17         ; r20 = byte alto de a
    andi r20, 0x80       ; r20 = bit de sinal de a
    mov r21, r17
    andi r21, 0x7C       ; r21 = 5 bits de expoente (parte alta)
    lsr r21
    lsr r21              ; r21 = expoente >> 2
    mov r22, r17
    andi r22, 0x03       ; r22 = 2 bits mais altos da mantissa
    lsl r22
    lsl r22
    lsl r22
    lsl r22
    lsl r22
    lsl r22              ; r22 = bits altos da mantissa deslocados
    or r22, r16          ; r22:r16 = mantissa completa

    ; Extrair componentes do segundo operando (b)
    mov r23, r19         ; r23 = byte alto de b
    andi r23, 0x80       ; r23 = bit de sinal de b
    mov r24, r19
    andi r24, 0x7C       ; r24 = 5 bits de expoente (parte alta)
    lsr r24
    lsr r24              ; r24 = expoente >> 2
    mov r25, r19
    andi r25, 0x03       ; r25 = 2 bits mais altos da mantissa
    lsl r25
    lsl r25
    lsl r25
    lsl r25
    lsl r25
    lsl r25              ; r25 = bits altos da mantissa deslocados
    or r25, r18          ; r25:r18 = mantissa completa

    ; Alinhar expoentes
    cp r21, r24
    breq exponents_equal
    brlo a_smaller
    
    ; Expoente de a é maior
    sub r21, r24         ; Diferença entre expoentes
    ; Ajustar mantissa de b
    lsr r25
    jmp exponents_equal
    
a_smaller:
    ; Expoente de b é maior
    sub r24, r21         ; Diferença entre expoentes
    ; Ajustar mantissa de a
    lsr r22
    
exponents_equal:
    ; Verificar sinais para soma/subtração
    cp r20, r23
    breq same_sign
    
    ; Sinais diferentes - realizar subtração
    jmp result_ready
    
same_sign:
    ; Sinais iguais - realizar soma
    add r16, r18         ; Somar bytes baixos da mantissa
    adc r22, r25         ; Somar bytes altos da mantissa com carry
    
result_ready:
    ; Reconstruir o número IEEE 754 de 16 bits
    mov r17, r20         ; Colocar bit de sinal
    
    ; Restaurar registradores
    pop r25
    pop r24
    pop r23
    pop r22
    pop r21
    pop r20
    ret

half_subtract:
    ret

half_multiply:
    ; Empilhar registradores
    push r20
    push r21
    push r22
    push r23
    push r24
    push r25
    
    ; Extrair sinal (XOR dos bits de sinal)
    mov r20, r17         ; Byte alto de a
    andi r20, 0x80       ; Bit de sinal de a
    mov r21, r19         ; Byte alto de b
    andi r21, 0x80       ; Bit de sinal de b
    eor r20, r21         ; r20 = sinal do resultado
    
    ; Extrair expoentes
    mov r21, r17
    andi r21, 0x7C       ; 5 bits de expoente de a
    lsr r21
    lsr r21              ; r21 = expoente normalizado
    
    mov r22, r19
    andi r22, 0x7C       ; 5 bits de expoente de b
    lsr r22
    lsr r22              ; r22 = expoente normalizado
    
    ; Somar expoentes e subtrair bias (15)
    add r21, r22
    subi r21, 15         ; r21 = expoente final
    
    ; Reconstruir o número IEEE 754 de 16 bits
    mov r17, r20         ; Colocar bit de sinal
    
    ; Restaurar registradores
    pop r25
    pop r24
    pop r23
    pop r22
    pop r21
    pop r20
    ret

half_divide:
    ret

integer_divide:
    ; Empilhar registradores
    push r20
    push r21
    push r22
    push r23
    
    ; Verificar divisão por zero
    mov r20, r18
    or r20, r19
    breq div_by_zero
    
    ; Salvar sinal
    mov r20, r16
    eor r20, r18         ; XOR para determinar o sinal do resultado
    andi r20, 0x80       ; Apenas o bit de sinal
    
    ; Resultado da divisão inteira em r16:r17
    ; Restaurar o sinal em r17
    andi r17, 0x7F       ; Limpar bit de sinal
    or r17, r20          ; Aplicar bit de sinal
    
    ; Restaurar registradores
    pop r23
    pop r22
    pop r21
    pop r20
    ret
    
div_by_zero:
    ; Tratar divisão por zero
    ldi r16, 0xFF       ; Indicar erro
    ldi r17, 0xFF
    
    ; Restaurar registradores
    pop r23
    pop r22
    pop r21
    pop r20
    ret

half_power:
    ret

half_modulo:
    ret
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
.equ SPH , 0x3E    ; Stack Pointer High
.equ SPL , 0x3D    ; Stack Pointer Low
.equ UBRR0L , 0xC4 ; Baud Rate Register Low
.equ UBRR0H , 0xC5 ; Baud Rate Register High
.equ UCSR0A , 0xC0 ; Control and Status Register A
.equ UCSR0B , 0xC1 ; Control and Status Register B
.equ UCSR0C , 0xC2 ; Control and Status Register C
.equ UDR0 , 0xC6   ; Registrador de dados UART0
;***************************************
.org 0x0000
    rjmp reset
    
reset:
    ; Configurar stack pointer
    ldi r16, 0x08
    out SPH, r16
    ldi r16, 0xFF
    out SPL, r16
    
    ; Configurar UART
    ldi r16, 103
    sts UBRR0L, r16
    ldi r16, 0
    sts UBRR0H, r16
    ldi r16, 8
    sts UCSR0B, r16
    ldi r16, 6
    sts UCSR0C, r16
    
    ; Delay inicial
    ldi r20, 255
delay_init_loop:
    dec r20
    brne delay_init_loop
    
    ; Enviar mensagem inicial
    ldi r16, 'C'
    rcall uart_envia_byte
    ldi r16, 'a'
    rcall uart_envia_byte
    ldi r16, 'l'
    rcall uart_envia_byte
    ldi r16, 'c'
    rcall uart_envia_byte
    ldi r16, 'u'
    rcall uart_envia_byte
    ldi r16, 'l'
    rcall uart_envia_byte
    ldi r16, 'a'
    rcall uart_envia_byte
    ldi r16, 'd'
    rcall uart_envia_byte
    ldi r16, 'o'
    rcall uart_envia_byte
    ldi r16, 'r'
    rcall uart_envia_byte
    ldi r16, 'a'
    rcall uart_envia_byte
    ldi r16, ' '
    rcall uart_envia_byte
    ldi r16, 'R'
    rcall uart_envia_byte
    ldi r16, 'P'
    rcall uart_envia_byte
    ldi r16, 'N'
    rcall uart_envia_byte
    ldi r16, ':'
    rcall uart_envia_byte
    ldi r16, 13
    rcall uart_envia_byte
    ldi r16, 10
    rcall uart_envia_byte
    ldi r16, 13
    rcall uart_envia_byte
    ldi r16, 10
    rcall uart_envia_byte
    
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
    ldi r16, '{char}'
    rcall uart_envia_byte
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
    rjmp loop_end

; Função para enviar um byte pela UART
uart_envia_byte:
    LDS R17, UCSR0A
    SBRS R17, 5
    RJMP uart_envia_byte
    STS UDR0, R16
    RET

; Função de delay em milissegundos
delay_ms:
    push r20
    push r21
    ldi r20, 100
delay_ms_outer:
    ldi r21, 255
delay_ms_inner:
    dec r21
    brne delay_ms_inner
    dec r20
    brne delay_ms_outer
    pop r21
    pop r20
    ret
""")
        # Adicionar rotinas para operações IEEE 754 half-precision
        adicionar_rotinas_ieee754(file)
    
    print("Arquivo Calculadora.asm gerado com sucesso!")

if __name__ == "__main__":
    main()