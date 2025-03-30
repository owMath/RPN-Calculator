@echo off
avr-as -mmcu=atmega328p -o calculadora.o calculadora.asm
avr-ld -o calculadora.elf calculadora.o
avr-objcopy -O ihex calculadora.elf calculadora.hex
avrdude -p atmega328p -c arduino -P COM3 -U flash:w:calculadora.hex
pause