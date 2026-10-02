# Estrutura pública do repositório

O KDP AI Factory usa branches para desenvolvimento e histórico, mas isso não deve criar dúvida para quem apenas quer usar o programa.

## Regra para usuários

A única porta de entrada para downloads é:

**GitHub → Releases → versão mais recente**

Não é necessário escolher uma branch ou baixar artefatos diretamente de GitHub Actions.

## Branches

- `main`: linha principal pública do projeto.
- `release/vX.Y.Z`: linha temporária de preparação/validação de uma release. É área de engenharia, não canal de download.
- `feature/*`: desenvolvimento de funcionalidades específicas. Não é versão pública.
- versões antigas: mantidas somente quando necessárias para histórico, manutenção ou recuperação.

## Releases

As releases são os pacotes oficiais distribuídos aos usuários.

Cada release deve apresentar claramente:

1. número da versão;
2. Windows;
3. Linux;
4. notas da versão;
5. instrução de instalação;
6. checksums quando aplicável.

## Regra de nomenclatura

Para novas versões públicas, usar tags no formato:

`vMAJOR.MINOR.PATCH`

Exemplo:

`v1.1.1`

A tag da release é o identificador público da versão. O usuário não precisa conhecer o nome da branch que produziu o build.

## Objetivo

O repositório pode continuar tecnicamente complexo por dentro, mas a experiência pública deve ser simples:

**abrir o repositório → clicar em Releases → baixar a versão mais recente → instalar.**
