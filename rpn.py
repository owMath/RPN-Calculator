"""
Alunos:
Gabriel Martins Vicente
Javier Agustin Aranibar González
Matheus Paul Lopuch
Rafael Bonfim Zacco

Grupo 04

Calculadora RPN para Arduino com suporte a float16
Este programa lê expressões RPN de um arquivo de texto, calcula os resultados
usando float16 e gera código Assembly que exibe tanto as expressões quanto seus resultados
com precisão de 16 bits.
"""

import sys  # Importa o módulo sys para acessar argumentos da linha de comando
import re   # Importa o módulo re para usar expressões regulares
import numpy as np  # Importa numpy para suporte a float16
import struct  # Para conversão binária precisa

class RPNCalculator:
    """
    Classe responsável por avaliar expressões RPN usando float16.
    
    Implementa um avaliador de expressões em notação polonesa reversa (RPN)
    com representação de números em precisão reduzida (float16).
    """
    
    def __init__(self):
        """
        Inicializa a calculadora RPN com suporte a float16.
        
        Cria:
        - Uma posição de memória (variável MEM)
        - Uma lista para armazenar resultados prévios (para uso do comando RES)
        """
        self.memory_value = np.float16(0.0)  # Usa float16 para memória
        self.previous_results = []           # Lista para armazenar resultados anteriores
    
    def _safe_float16_op(self, operation):
        """
        Executa operações com tratamento de overflow/underflow para float16.
        
        Args:
            operation (callable): Função que retorna o resultado da operação
            
        Returns:
            np.float16: Resultado da operação com tratamento de limites
        """
        try:
            result = operation()
            return np.float16(result)
        except OverflowError:
            print("Aviso: Overflow detectado. Retornando valor máximo de float16.")
            return np.float16(np.finfo(np.float16).max)
        except UnderflowError:
            print("Aviso: Underflow detectado. Retornando zero.")
            return np.float16(0.0)
    
    def evaluate_expression(self, expression):
        """
        Avalia uma expressão RPN e retorna o resultado em float16.
        
        Args:
            expression (str): A expressão RPN a ser avaliada
            
        Returns:
            np.float16: O resultado da expressão
        """
        # Remove parênteses externos se existirem
        if expression.startswith('(') and expression.endswith(')'):
            expression = expression[1:-1].strip()
        
        # Verifica comandos especiais:
        
        # Comando (N RES) - retorna o resultado N linhas anteriores
        res_match = re.match(r'^(\d+)\s+RES$', expression)
        if res_match:
            n = int(res_match.group(1))  # Extrai o número N do comando
            # Verifica se o índice N é válido
            if n > len(self.previous_results) or n == 0:
                print(f"Aviso: Tentativa de acessar resultado inexistente (linha -{n})")
                return np.float16(0.0)
            # Retorna o resultado N posições atrás na lista de resultados
            return self.previous_results[len(self.previous_results) - n ]
        
        # Comando (V MEM) - armazena o valor V na memória
        mem_store_match = re.match(r'^([\d.]+)\s+MEM$', expression)
        if mem_store_match:
            # Converte e armazena como float16
            self.memory_value = np.float16(float(mem_store_match.group(1)))
            return self.memory_value
        
        # Comando (MEM) - retorna o valor armazenado na memória
        if expression == 'MEM':
            return self.memory_value
        
        # Caso não seja um comando especial, analisa como expressão RPN normal
        
        # Divide a expressão em tokens, cuidando com subexpressões aninhadas entre parênteses
        tokens = []
        current_token = ""
        paren_level = 0  # Controla o nível de aninhamento de parênteses
        
        # Percorre cada caractere da expressão
        for char in expression:
            if char == '(' and paren_level == 0:
                # Início de uma subexpressão no nível zero
                if current_token:
                    tokens.append(current_token.strip())
                    current_token = ""
                current_token += char
                paren_level += 1
            elif char == ')' and paren_level == 1:
                # Fim de uma subexpressão no nível um
                current_token += char
                paren_level -= 1
                tokens.append(current_token.strip())
                current_token = ""
            elif char == '(':
                # Início de uma subexpressão aninhada
                current_token += char
                paren_level += 1
            elif char == ')':
                # Fim de uma subexpressão aninhada
                current_token += char
                paren_level -= 1
            elif char.isspace() and paren_level == 0:
                # Espaço fora de subexpressões serve como separador de tokens
                if current_token:
                    tokens.append(current_token.strip())
                    current_token = ""
            else:
                # Adiciona o caractere ao token atual
                current_token += char
        
        # Adiciona o último token se existir
        if current_token:
            tokens.append(current_token.strip())
        
        # Pilha para simular a execução das operações RPN
        stack = []
        
        # Processa cada token na expressão
        for token in tokens:
            if token.startswith('('):
                # Subexpressão aninhada - avalia recursivamente
                result = self.evaluate_expression(token)
                stack.append(result)
            elif token == '+':
                # Operação de adição
                if len(stack) < 2:
                    print("Erro: Pilha insuficiente para adição")
                    return np.float16(0.0)
                b = stack.pop()  # Segundo operando
                a = stack.pop()  # Primeiro operando
                result = self._safe_float16_op(lambda: a + b)
                stack.append(result)
            elif token == '-':
                # Operação de subtração
                if len(stack) < 2:
                    print("Erro: Pilha insuficiente para subtração")
                    return np.float16(0.0)
                b = stack.pop()
                a = stack.pop()
                result = self._safe_float16_op(lambda: a - b)
                stack.append(result)
            elif token == '*':
                # Operação de multiplicação
                if len(stack) < 2:
                    print("Erro: Pilha insuficiente para multiplicação")
                    return np.float16(0.0)
                b = stack.pop()
                a = stack.pop()
                result = self._safe_float16_op(lambda: a * b)
                stack.append(result)
            elif token == '|':
                # Operação de divisão real
                if len(stack) < 2:
                    print("Erro: Pilha insuficiente para divisão")
                    return np.float16(0.0)
                b = stack.pop()
                a = stack.pop()
                if b == 0:
                    print("Aviso: Divisão por zero detectada")
                    stack.append(np.float16(float('inf')))  # Retorna infinito
                else:
                    result = self._safe_float16_op(lambda: a / b)
                    stack.append(result)
            elif token == '/':
                # Operação de divisão de inteiros
                if len(stack) < 2:
                    print("Erro: Pilha insuficiente para divisão de inteiros")
                    return np.float16(0.0)
                b = stack.pop()
                a = stack.pop()
                if b == 0:
                    print("Aviso: Divisão por zero detectada")
                    stack.append(np.float16(float('inf')))
                else:
                    # Converte para inteiro e depois de volta para float16
                    result = self._safe_float16_op(lambda: int(a) // int(b))
                    stack.append(result)
            elif token == '%':
                # Operação de resto da divisão
                if len(stack) < 2:
                    print("Erro: Pilha insuficiente para resto da divisão")
                    return np.float16(0.0)
                b = stack.pop()
                a = stack.pop()
                if b == 0:
                    print("Aviso: Divisão por zero detectada")
                    stack.append(np.float16(0.0))
                else:
                    # Converte para inteiro e depois de volta para float16
                    result = self._safe_float16_op(lambda: int(a) % int(b))
                    stack.append(result)
            elif token == '^':
                # Operação de potenciação
                if len(stack) < 2:
                    print("Erro: Pilha insuficiente para potenciação")
                    return np.float16(0.0)
                b = stack.pop()  # Expoente
                a = stack.pop()  # Base
                # Verifica se o expoente é inteiro positivo conforme requisito
                if b != int(b) or b < 0:
                    print(f"Aviso: Expoente deve ser inteiro positivo: {b}")
                    b = max(0, int(b))  # Ajusta para inteiro positivo
                result = self._safe_float16_op(lambda: a ** b)
                stack.append(result)
            elif token == 'MEM':  # Adicionamos esta condição aqui
                stack.append(self.memory_value)  # Coloca o valor da memória na pilha
            else:
                # Considera como número e adiciona à pilha
                try:
                    # Converte diretamente para float16
                    stack.append(np.float16(float(token)))
                except ValueError:
                    print(f"Aviso: Token não reconhecido: {token}")
                    stack.append(np.float16(0.0))  # Valor padrão para tokens não reconhecidos
        
        # Ao final, deve haver apenas um valor na pilha (o resultado)
        if len(stack) == 1:
            return stack[0]
        else:
            print(f"Aviso: Expressão malformada, restaram {len(stack)} itens na pilha")
            return np.float16(0.0) if not stack else stack[-1]  # Retorna 0 ou o topo da pilha


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
            expressions = [line.strip() for line in file if line.strip()]
        return expressions
    except FileNotFoundError:
        print(f"Erro: Arquivo '{filename}' não encontrado.")
        sys.exit(1)  # Encerra o programa com código de erro


def get_float16_precision_string(value):
    """
    Converte um float16 para string com precisão exata de 16 bits.
    
    Args:
        value (np.float16): O valor float16 a ser convertido
        
    Returns:
        str: String representando o valor com precisão de float16
    """
    # Extrai os bits de float16
    bits = np.float16(value).view(np.uint16)
    
    # Extrai os componentes
    sign_bit = (bits >> 15) & 0x1
    exponent = (bits >> 10) & 0x1F
    mantissa = bits & 0x3FF
    
    if exponent == 0 and mantissa == 0:
        # Zero
        return "0.0" if sign_bit == 0 else "-0.0"
    elif exponent == 0x1F:
        # Infinito ou NaN
        if mantissa == 0:
            return "inf" if sign_bit == 0 else "-inf"
        else:
            return "nan"
    
    # Números normais e denormalizados
    sign = '-' if sign_bit else ''
    
    if exponent == 0:
        # Denormalizado
        actual_exponent = -14
        actual_mantissa = mantissa / 1024.0
    else:
        # Normalizado
        actual_exponent = exponent - 15
        actual_mantissa = 1.0 + mantissa / 1024.0
    
    # Calcula o valor decimal
    value_decimal = actual_mantissa * (2.0 ** actual_exponent)
    
    # Formata com precisão limitada a ~3-4 dígitos significativos (float16)
    # Limita a 6 caracteres total para números pequenos
    if abs(value_decimal) < 0.001 or abs(value_decimal) >= 10000:
        # Notação científica para números muito grandes ou pequenos
        fmt_str = f"{sign}{value_decimal:.4e}"
    else:
        # Notação decimal com precisão limitada
        precision = 4 - len(str(int(abs(value_decimal))))
        precision = max(0, precision)  # Evita precisão negativa
        fmt_str = f"{sign}{value_decimal:.{precision}f}"
    
    # Remove zeros à direita se for um valor decimal
    if '.' in fmt_str and 'e' not in fmt_str:
        fmt_str = fmt_str.rstrip('0').rstrip('.')
        if fmt_str == '-0' or fmt_str == '':
            fmt_str = '0'
    
    return fmt_str


def generate_assembly(expressions, results):
    """
    Gera código Assembly para Arduino que mostra as expressões e seus resultados.
    
    O código Assembly gerado configura a UART para comunicação serial
    e envia os textos das expressões e seus resultados com precisão de float16.
    
    Args:
        expressions (list): Lista de expressões RPN
        results (list): Lista de resultados calculados
        
    Returns:
        list: Linhas de código Assembly para Arduino
    """
    # Cabeçalho do código Assembly - configuração inicial
    assembly_code = [
        "; Calculadora RPN para Arduino - Expressões e Resultados (float16)",
        "",
        ".global main",  # Ponto de entrada do programa
        "",
        ".section .text",  # Seção de código
        "",
        "main:",
        "    ; Configurar pilha",
        "    ldi r16, lo8(0x08FF)",  # Byte baixo do endereço da pilha
        "    out 0x3D, r16",          # Carrega em SPL (Stack Pointer Low)
        "    ldi r16, hi8(0x08FF)",  # Byte alto do endereço da pilha
        "    out 0x3E, r16",          # Carrega em SPH (Stack Pointer High)
        "",
        "    ; Configurar UART",
        "    ldi r16, 103",           # Define taxa de baud (9600 bps)
        "    sts 0xC4, r16",          # UBRR0L
        "    ldi r16, 0",
        "    sts 0xC5, r16",          # UBRR0H
        "    ",
        "    ldi r16, 0x08",          # Habilita o transmissor
        "    sts 0xC1, r16",          # UCSR0B
        "    ",
        "    ldi r16, 0x06",          # Configura formato (8N1)
        "    sts 0xC2, r16",          # UCSR0C
        "    ",
        "    ; Atraso inicial",
        "    rcall delay",            # Chama a rotina de atraso
        "    ",
        "    ; Mensagem de início",
        "    ldi r16, 'R'",           # Carrega caractere 'R'
        "    rcall uart_send",        # Envia pela UART
        "    ldi r16, 'P'",
        "    rcall uart_send",
        "    ldi r16, 'N'",
        "    rcall uart_send",
        "    ldi r16, ' '",
        "    rcall uart_send",
        "    ldi r16, 'F'",
        "    rcall uart_send",
        "    ldi r16, '1'",
        "    rcall uart_send",
        "    ldi r16, '6'",
        "    rcall uart_send",
        "    rcall print_newline",    # Insere nova linha
        ""
    ]
    
    # Adiciona código para mostrar cada expressão e seu resultado
    for idx, (expr, result) in enumerate(zip(expressions, results)):
        # Prepara o resultado como string com precisão exata de float16
        result_str = get_float16_precision_string(result)
        
        # Adiciona comentário e imprime o número da expressão
        assembly_code.extend([
            f"    ; Expressão {idx+1}: {expr} = {result_str}",
            "    ldi r16, 'E'",
            "    rcall uart_send",
            "    ldi r16, 'x'",
            "    rcall uart_send",
            "    ldi r16, 'p'",
            "    rcall uart_send"
        ])
        
        # Imprime o número da expressão (limitado de 1 a 9)
        if idx < 9:  # Números 1-9 são seguros para imprimir
            assembly_code.extend([
                f"    ldi r16, '{idx+1}'",
                "    rcall uart_send"
            ])
        else:
            # Para mais de 9 expressões, usa '+' como indicador
            assembly_code.extend([
                "    ldi r16, '+'",
                "    rcall uart_send"
            ])
        
        # Imprime separador
        assembly_code.extend([
            "    ldi r16, ':'",
            "    rcall uart_send",
            "    ldi r16, ' '",
            "    rcall uart_send"
        ])
        
        # Imprime a expressão (caractere por caractere)
        # Filtra para manter apenas caracteres seguros
        safe_chars = "()+-*/|%^0123456789. MESR"
        expr_clean = ''.join(c for c in expr if c in safe_chars)
        
        for char in expr_clean:
            assembly_code.extend([
                f"    ldi r16, '{char}'",
                "    rcall uart_send"
            ])
        
        # Imprime o sinal de igual
        assembly_code.extend([
            "    ldi r16, ' '",
            "    rcall uart_send",
            "    ldi r16, '='",
            "    rcall uart_send",
            "    ldi r16, ' '",
            "    rcall uart_send"
        ])
        
        # Imprime o resultado formatado com precisão float16
        for char in result_str:
            # Imprime apenas caracteres seguros
            if char in "0123456789.-+einf":
                assembly_code.extend([
                    f"    ldi r16, '{char}'",
                    "    rcall uart_send"
                ])
        
        # Adiciona nova linha após cada expressão
        assembly_code.append("    rcall print_newline")
    
    # Adiciona código de finalização do programa
    assembly_code.extend([
        "",
        "    ; Programa concluído",
        "    ldi r16, 'F'",
        "    rcall uart_send",
        "    ldi r16, 'I'",
        "    rcall uart_send",
        "    ldi r16, 'M'",
        "    rcall uart_send",
        "    rcall print_newline",
        "",
        "    ; Loop infinito para manter o programa rodando",
        "loop:",
        "    rjmp loop",  # Jump relativo para o próprio label
        "",
        "; Rotina para enviar um caractere pela UART",
        "uart_send:",
        "wait_tx:",
        "    lds r17, 0xC0",    # Carrega UCSR0A em r17
        "    sbrs r17, 5",       # Verifica se UDRE0 está setado (buffer de transmissão vazio)
        "    rjmp wait_tx",      # Se não, aguarda
        "    ",
        "    sts 0xC6, r16",     # Envia byte para UDR0 (buffer de transmissão)
        "    ret",                # Retorna da sub-rotina
        "",
        "; Rotina de atraso simples",
        "delay:",
        "    ldi r18, 200",       # Contador externo
        "d1:",
        "    ldi r19, 200",       # Contador interno
        "d2:",
        "    dec r19",            # Decrementa contador interno
        "    brne d2",            # Continua se não for zero
        "    dec r18",            # Decrementa contador externo
        "    brne d1",            # Continua se não for zero
        "    ret",                # Retorna da sub-rotina
        "",
        "; Rotina para enviar nova linha",
        "print_newline:",
        "    ; Enviar CR (Carriage Return)",
        "    ldi r16, 13",
        "    rcall uart_send",
        "    ; Enviar LF (Line Feed)",
        "    ldi r16, 10",
        "    rcall uart_send",
        "    ret"                 # Retorna da sub-rotina
    ])
    
    return assembly_code


def main():
    """
    Função principal que orquestra o fluxo do programa:
    1. Lê o arquivo de entrada com expressões RPN
    2. Avalia cada expressão e armazena os resultados
    3. Gera código Assembly para Arduino
    4. Exibe resultados e salva código Assembly em arquivo
    """
    # Verifica se o nome do arquivo foi fornecido na linha de comando
    if len(sys.argv) != 2:
        print("Uso: python rpn_calculator.py <arquivo>")
        sys.exit(1)
    
    filename = sys.argv[1]  # Pega o nome do arquivo da linha de comando
    
    # Lê as expressões do arquivo
    expressions = read_expressions_file(filename)
    
    # Instancia a calculadora e processa as expressões
    calculator = RPNCalculator()
    results = []
    
    for expr in expressions:
        # Avalia cada expressão
        result = calculator.evaluate_expression(expr)
        results.append(result)
        # Armazena o resultado para uso do comando RES
        calculator.previous_results.append(result)
    
    # Exibe as expressões e resultados no console com precisão de float16
    print(f"Expressões e resultados de {filename}:")
    for idx, (expr, result) in enumerate(zip(expressions, results)):
        # Formata o resultado com precisão específica de float16
        result_str = get_float16_precision_string(result)
        print(f"{idx+1}. {expr} = {result_str}")
    
    # Gera o código Assembly
    assembly_code = generate_assembly(expressions, results)
    
    # Escreve o código Assembly em um arquivo
    output_filename = "rpn_calculator.S"
    with open(output_filename, 'w') as file:
        for line in assembly_code:
            file.write(line + '\n')
    
    print(f"\nCódigo Assembly gerado em {output_filename}")
    
    # Exibe instruções de compilação para o usuário
    print("\nPara compilar e gravar no Arduino:")
    print("1. Compilar o código Assembly:")
    print('   avr-gcc -mmcu=atmega328p -o rpn_calculator.elf rpn_calculator.S')
    print('2. Converta para formato HEX:')
    print('   avr-objcopy -O ihex rpn_calculator.elf rpn_calculator.hex')
    print('3. Grave no Arduino:')
    print('   avrdude -C "avrdude.conf" -p atmega328p -c arduino -P COMx -b 115200 -U flash:w:rpn_calculator.hex')
    print('   (Substitua COMx pela porta do Arduino)')

# Ponto de entrada do programa
if __name__ == "__main__":
    main()
