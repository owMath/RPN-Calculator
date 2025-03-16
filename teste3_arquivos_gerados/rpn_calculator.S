; Calculadora RPN para Arduino - Expressões e Resultados

.global main

.section .text

main:
    ; Configurar pilha
    ldi r16, lo8(0x08FF)
    out 0x3D, r16
    ldi r16, hi8(0x08FF)
    out 0x3E, r16

    ; Configurar UART
    ldi r16, 103
    sts 0xC4, r16
    ldi r16, 0
    sts 0xC5, r16
    
    ldi r16, 0x08
    sts 0xC1, r16
    
    ldi r16, 0x06
    sts 0xC2, r16
    
    ; Atraso inicial
    rcall delay
    
    ; Mensagem de início
    ldi r16, 'R'
    rcall uart_send
    ldi r16, 'P'
    rcall uart_send
    ldi r16, 'N'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, 'C'
    rcall uart_send
    ldi r16, 'a'
    rcall uart_send
    ldi r16, 'l'
    rcall uart_send
    ldi r16, 'c'
    rcall uart_send
    rcall print_newline

    ; Expressão 1: (2.5 1.5 +) = 4.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '2'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '5'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '5'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '+'
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '4'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline
    ; Expressão 2: (10.0 5.0 -) = 5.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '2'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '5'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '-'
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '5'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline
    ; Expressão 3: (4.0 5.0 *) = 20.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '3'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '4'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '5'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '*'
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '2'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline
    ; Expressão 4: (20.0 4.0 |) = 5.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '4'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '2'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '4'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '|'
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '5'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline
    ; Expressão 5: (21.0 4.0 /) = 5.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '5'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '2'
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '4'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '/'
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '5'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline
    ; Expressão 6: (21.0 4.0 %) = 1.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '6'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '2'
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '4'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '%'
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline
    ; Expressão 7: (2.0 4.0 ^) = 16.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '7'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '2'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '4'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '^'
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, '6'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline
    ; Expressão 8: ((3.0 2.0 *) (1.0 1.0 +) +) = 8.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '8'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '3'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '2'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '*'
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '+'
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '+'
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '8'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline
    ; Expressão 9: (100.0 MEM) = 100.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '9'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline
    ; Expressão 10: (MEM) = 100.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '+'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline
    ; Expressão 11: (MEM 50.0 -) = -50.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '+'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '5'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '-'
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '-'
    rcall uart_send
    ldi r16, '5'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline
    ; Expressão 12: (1 RES) = 100.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '+'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline
    ; Expressão 13: (2 RES) = 100.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '+'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '2'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline
    ; Expressão 14: ((1 RES) (2 RES) +) = 50.0
    ldi r16, 'E'
    rcall uart_send
    ldi r16, 'x'
    rcall uart_send
    ldi r16, 'p'
    rcall uart_send
    ldi r16, '+'
    rcall uart_send
    ldi r16, ':'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '1'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '('
    rcall uart_send
    ldi r16, '2'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '+'
    rcall uart_send
    ldi r16, ')'
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '='
    rcall uart_send
    ldi r16, ' '
    rcall uart_send
    ldi r16, '5'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    ldi r16, '.'
    rcall uart_send
    ldi r16, '0'
    rcall uart_send
    rcall print_newline

    ; Programa concluído
    ldi r16, 'F'
    rcall uart_send
    ldi r16, 'I'
    rcall uart_send
    ldi r16, 'M'
    rcall uart_send
    rcall print_newline

    ; Loop infinito para manter o programa rodando
loop:
    rjmp loop

; Rotina para enviar um caractere pela UART
uart_send:
wait_tx:
    lds r17, 0xC0
    sbrs r17, 5
    rjmp wait_tx
    
    sts 0xC6, r16
    ret

; Rotina de atraso simples
delay:
    ldi r18, 200
d1:
    ldi r19, 200
d2:
    dec r19
    brne d2
    dec r18
    brne d1
    ret

; Rotina para enviar nova linha
print_newline:
    ; Enviar CR (Carriage Return)
    ldi r16, 13
    rcall uart_send
    ; Enviar LF (Line Feed)
    ldi r16, 10
    rcall uart_send
    ret
