# Licenciamento

O KDP AI Factory tem código aberto, mas a versão oficial possui uma política de uso: uma instalação/máquina pode criar um livro gratuitamente. Depois disso, é necessária uma licença vitalícia.

## O que o open source permite

Qualquer pessoa pode estudar, modificar e fazer fork do código. Não existe mecanismo técnico capaz de impedir que um fork altere a própria lógica de licença.

Por isso, a proteção da versão oficial é baseada em:

- servidor oficial de licenças;
- Machine ID com hash;
- licença associada à instalação;
- assinatura digital;
- chaves privadas mantidas somente no servidor.

## Machine ID

O cliente combina sinais do sistema e calcula um SHA-256. Os identificadores brutos não são usados como identificador público.

O MAC address, sozinho, não é considerado uma proteção suficiente porque pode ser alterado.

## Trial

1. A primeira execução cria um Machine ID.
2. O primeiro projeto é permitido.
3. A criação de um segundo livro exige licença.
4. O cliente registra a instalação no serviço oficial quando o serviço está configurado.

## Licença vitalícia

A licença oficial é emitida pelo servidor depois da confirmação do pagamento.

O cliente envia o Machine ID e recebe um token/licença assinado. A chave privada utilizada para assinar licenças nunca fica no aplicativo.

## Pagamentos

O fluxo oficial será:

1. Cliente escolhe USDT ou BNB.
2. Cliente recebe a carteira oficial e a rede BSC.
3. Cliente efetua o pagamento.
4. Servidor verifica o pagamento.
5. Servidor confere valor, ativo, rede, endereço de destino e hash.
6. A transação precisa atingir o estado de confirmação definido pelo servidor.
7. O servidor emite a licença.
8. A licença é vinculada ao Machine ID.

Credenciais da Bybit são exclusivas do servidor. Nunca coloque API key ou API secret no cliente ou no GitHub.

## Limitações

O sistema pode proteger a versão oficial contra reutilização casual do trial e contra falsificação de licenças oficiais, mas não pode impedir alguém de criar uma versão modificada do código aberto.
