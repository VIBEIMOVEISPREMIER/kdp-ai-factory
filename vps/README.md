# KDP AI Factory — GPU/VPS companion

O desktop continua leve e funciona em PCs modestos. Quando a máquina não tiver
GPU suficiente, o usuário pode executar o KDP AI Engine Server em uma VPS
com GPU e apontar o aplicativo para ela.

## VPS recomendada

Para testes e uso individual, uma GPU NVIDIA com 24 GB de VRAM é um ponto
de partida confortável para geração de imagens. O Runpod oferece Pods com RTX
4090 24 GB e cobrança por segundo; preços e disponibilidade variam. Consulte
a página oficial antes de contratar.

## Arquitetura

PC do cliente -> KDP-AI-Factory.exe -> HTTPS/token -> VPS GPU -> Ollama/ComfyUI/modelos

## Configuração

1. Crie uma VPS/Pod Linux com GPU NVIDIA e armazenamento persistente.
2. Instale Docker + NVIDIA Container Toolkit, ou use uma imagem NVIDIA pronta.
3. Copie esta pasta para o servidor.
4. Edite .env e defina um token forte.
5. Suba os serviços com docker compose up -d.
6. Teste /health.
7. No KDP AI Factory, informe a URL HTTPS e o token.

## Executáveis de IA

A distribuição pode manter uma pasta AI-ENGINES separada do executável
principal. Ela guarda os lançadores/configurações do KDP e documentação para
Ollama/ComfyUI. Binários e pesos de terceiros devem ser obtidos diretamente
de seus projetos/licenças e não são incorporados automaticamente ao GitHub.

Assim o KDP-AI-Factory.exe continua leve e o pacote de engines pode ser movido
para a VPS sem reinstalar o aplicativo principal.
