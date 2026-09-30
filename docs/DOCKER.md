# KDP AI Factory — Docker First

O modo principal de execução do KDP AI Factory é Docker. No Windows, a ideia é instalar apenas o Docker Desktop; Python, Node, Ollama e ComfyUI ficam encapsulados nos containers.

## Requisito

- Docker Desktop com Docker Compose v2.
- Para aceleração por GPU, a configuração de GPU do Docker Desktop/WSL2 e o driver compatível precisam estar funcionando no Windows.

## Iniciar

Na raiz do repositório:

~~~powershell
docker compose up -d --build
~~~

Ou:

~~~powershell
.\scripts\docker-up.ps1
~~~

Depois abra:

**http://localhost:8080**

## Parar

~~~powershell
docker compose down
~~~

Ou:

~~~powershell
.\scripts\docker-down.ps1
~~~

## Logs

~~~powershell
docker compose logs -f
~~~

Ou:

~~~powershell
.\scripts\docker-logs.ps1
~~~

## Arquitetura

- dashboard — React/Vite servido por Nginx.
- api — FastAPI e motor editorial.
- ollama — inferência local de texto.
- comfyui — geração visual por workflows.
- volumes Docker — projetos, banco SQLite, modelos e saídas persistem mesmo quando os containers são recriados.

O navegador acessa somente o dashboard. O Nginx encaminha /api/* para o serviço FastAPI dentro da rede Docker.

## Modelos

As imagens Docker não incluem todos os pesos de IA. Os modelos são dados grandes e ficam nos volumes persistentes.

O Ollama pode baixar modelos explicitamente pelo próprio container:

~~~powershell
docker compose exec ollama ollama pull llama3.2
docker compose exec ollama ollama list
~~~

Isso evita instalar Ollama no Windows.

Os modelos do ComfyUI ficam no volume comfyui_models.

## GPU

O stack funciona em modo CPU quando o hardware/container não expõe GPU, mas geração de imagens e modelos grandes podem ficar muito mais lentos.

A aceleração NVIDIA depende do suporte de GPU do Docker Desktop/WSL2 e do driver do host. Não instale Python, Node, Ollama ou ComfyUI nativamente apenas para usar o Factory.

## Dados persistentes

Os volumes são:

- kdp_factory_data
- ollama_data
- comfyui_models
- comfyui_custom_nodes
- comfyui_output

docker compose down preserva esses volumes. Para apagar também os dados, use conscientemente:

~~~powershell
docker compose down -v
~~~

## Diagnóstico

A página Sistema / IA consulta o diagnóstico do próprio container e os serviços Docker internos.

Em Docker, comandos nativos do Windows não são necessários para a execução do Factory.

## Desenvolvimento nativo

Os scripts antigos de Python/Node continuam no repositório para desenvolvimento avançado, mas não são o caminho recomendado para uso normal. O fluxo principal é Docker.
