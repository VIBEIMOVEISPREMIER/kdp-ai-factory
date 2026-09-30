# KDP AI Factory — instalação no Windows

O projeto pode ser executado nativamente no Windows. Docker não é obrigatório.

## Requisitos

- Windows 10/11 64-bit
- Python 3.11 ou superior
- Git
- Node.js 20 LTS ou superior para desenvolvimento do dashboard
- Espaço em disco suficiente para projetos e modelos

Ollama e ComfyUI são componentes opcionais. Modelos grandes não são baixados automaticamente.

## 1. Verificar programas

~~~powershell
python --version
node --version
npm --version
git --version
~~~

## 2. Criar ambiente Python

~~~powershell
py -3.11 -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
~~~

## 3. Inicializar

~~~powershell
kdp-factory init
kdp-factory doctor
~~~

## 4. Executar a API

~~~powershell
kdp-factory start
~~~

A API ficará em http://127.0.0.1:8000.

## 5. Dashboard

Em outro PowerShell:

~~~powershell
cd apps/dashboard
npm install
npm run dev
~~~

O Vite exibirá o endereço local.

## 6. Primeiro livro

Abra o dashboard e selecione Novo livro. A edição oficial permite um livro gratuito por instalação/máquina. Depois disso, a criação de novos livros exige licença.

## 7. Diagnóstico

~~~powershell
kdp-factory doctor
kdp-factory models
kdp-factory validate caminho\book_spec.json
~~~

## IA

Ollama e ComfyUI são opcionais. Instale-os apenas quando a máquina tiver recursos suficientes.
