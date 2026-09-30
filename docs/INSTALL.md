# Instalação no Windows

## Requisitos

- Windows 10/11
- Python 3.11 ou superior
- Git
- Node.js será necessário quando o dashboard React for ativado

## Instalação

Abra PowerShell na pasta do projeto:

    .\scripts\install.ps1

Depois:

    .\.venv\Scripts\kdp-factory.exe doctor

Para iniciar:

    .\scripts\start.ps1

A API ficará em:

    http://127.0.0.1:8000

## Criar projeto

    .\.venv\Scripts\kdp-factory.exe new "Meu Primeiro Livro" --book-type childrens --language pt-BR

## Listar projetos

    .\.venv\Scripts\kdp-factory.exe list
