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

## GPU NVIDIA

O Compose do Factory já reserva a GPU NVIDIA para **Ollama e ComfyUI**. No Windows, o Docker Desktop precisa estar usando **WSL 2** e a GPU precisa estar disponível para containers. O Docker documenta GPU-PV para NVIDIA no Windows e o Compose usa uma reserva `driver: nvidia`, `count: all`, `capabilities: [gpu]`. citeturn0search0turn0search1

Primeiro teste a GPU diretamente no Docker:

~~~powershell
docker run --rm --gpus all nvidia/cuda:12.9.0-base-ubuntu22.04 nvidia-smi
~~~

Se esse comando mostrar sua placa NVIDIA, o passthrough da GPU está funcionando. Depois recrie o Factory:

~~~powershell
docker compose down
docker compose up -d --build
~~~

Confira o Ollama:

~~~powershell
docker compose exec ollama nvidia-smi
docker compose logs ollama --tail=100
~~~

Não instale Python, Node, Ollama ou ComfyUI nativamente apenas para usar o Factory. O suporte GPU do Docker Desktop no Windows depende do backend WSL 2 e de drivers NVIDIA compatíveis. citeturn0search0turn0search2

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
