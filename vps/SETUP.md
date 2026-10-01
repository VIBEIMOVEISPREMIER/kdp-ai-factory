# KDP AI Engine Server — setup de VPS

## Perfil recomendado
- GPU NVIDIA: RTX 4090 24 GB para começar
- RAM: 32 GB ou mais
- SSD: 100 GB ou mais
- Linux com suporte NVIDIA
- HTTPS/reverse proxy recomendado para uso pela internet

## 1. Instale os engines
Instale Ollama e ComfyUI na VPS seguindo as instruções oficiais dos respectivos projetos.
O KDP AI Engine Server não redistribui binários ou pesos de terceiros.

## 2. Configure o servidor
Na pasta vps:

    cp .env.example .env

Edite:

    KDP_ENGINE_TOKEN=um-token-longo-e-secreto
    KDP_ENGINE_PORT=8189
    OLLAMA_URL=http://127.0.0.1:11434
    COMFYUI_URL=http://127.0.0.1:8188

## 3. Inicie o gateway

    docker compose up -d

O gateway ficará em:

    http://IP-DA-VPS:8189/health

## 4. Segurança
Não exponha a porta sem autenticação. Para produção, coloque HTTPS com um reverse proxy
(Caddy, Nginx ou equivalente) e mantenha KDP_ENGINE_TOKEN secreto.

## 5. Conectar no aplicativo
No Windows, configure:

    KDP_ENGINE_URL=https://SEU-DOMINIO
    KDP_ENGINE_TOKEN=SEU_TOKEN

Com KDP_ENGINE_URL preenchido, o Factory usa o engine remoto para texto e imagens.

## 6. Imagens
O endpoint de imagem recebe um workflow JSON do ComfyUI. O workflow deve usar
{{prompt}} e opcionalmente {{seed}} nos campos que você quer substituir.

## 7. Custos
GPU é cobrada pelo provedor. Desligue/termine a instância quando não estiver usando,
e use armazenamento persistente para não perder modelos.
