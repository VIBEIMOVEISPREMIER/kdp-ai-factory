# KDP AI Factory

A local-first, open-source AI publishing platform designed to help users create, edit, illustrate, format, validate, and prepare books for Amazon KDP.

## Visão

O KDP AI Factory não é apenas um gerador de livros de colorir. Ele foi projetado como uma fábrica editorial modular para livros infantis, ficção, educativos, apostilas, workbooks, diários, planners, cadernos, receitas, poesia, atividades e projetos personalizados.

## Princípios

- Docker-first: execução encapsulada em containers.
- Sem instalação nativa obrigatória de Python, Node, Ollama ou ComfyUI.
- IA local sempre que possível.
- Sem API paga de IA obrigatória.
- Sem créditos artificiais para geração de imagens.
- Múltiplos modelos locais.
- Arquitetura multilíngue.
- Dashboard visual para iniciantes e CLI para uso avançado.
- Projetos persistentes e checkpoints.
- Validação e exportação orientadas ao KDP.
- Arquitetura modular para trocar modelos e provedores.

## Status

🚧 Em desenvolvimento ativo — núcleo 1.0 e infraestrutura Docker-first já estruturados.

## Execução recomendada no Windows

O fluxo normal usa somente Docker Desktop no host.

~~~powershell
docker compose up -d --build
~~~

Depois abra:

**http://localhost:8080**

Ou use o script:

~~~powershell
.\scripts\docker-up.ps1
~~~

Para parar:

~~~powershell
docker compose down
~~~

Para logs:

~~~powershell
docker compose logs -f
~~~

Documentação completa: [docs/DOCKER.md](docs/DOCKER.md)

## Arquitetura Docker

- **dashboard** — React + TypeScript + Vite, servido por Nginx.
- **api** — FastAPI + motor editorial Python.
- **ollama** — servidor de modelos locais de texto.
- **comfyui** — engine local de geração visual.
- **volumes Docker** — banco, projetos, modelos e resultados persistem fora do ciclo de vida dos containers.

O navegador conversa com o dashboard em localhost. O Nginx faz o proxy interno de /api para o FastAPI.

## IA local

Ollama é usado para texto e ComfyUI para workflows visuais. Os pesos dos modelos são grandes e, por isso, não são embutidos no código do projeto.

Exemplo para instalar um modelo no container Ollama:

~~~powershell
docker compose exec ollama ollama pull llama3.2
~~~

Nenhuma instalação nativa do Ollama é necessária.

A aceleração por GPU é opcional e depende do suporte de GPU do Docker Desktop/WSL2 e do driver do host.

## Stack

- Web: React + TypeScript
- Backend/core: Python + FastAPI
- Texto local: Ollama
- Imagens locais: ComfyUI
- Documentos: PDF/EPUB/DOCX
- Banco: SQLite inicialmente
- CLI: Typer
- CI: GitHub Actions

## Importante sobre publicação KDP

O projeto prepara conteúdo, arquivos, metadados e validações para o fluxo KDP. A publicação automática fica isolada porque a disponibilidade e as regras da interface da Amazon podem mudar; o sistema não depende de uma suposta API pública de publicação completa.

## Desenvolvimento nativo

Os scripts de instalação nativa permanecem para desenvolvedores que quiserem trabalhar fora dos containers. Eles não fazem parte do caminho recomendado para uso normal.

## Licença

A licença final será definida antes da primeira versão pública.
