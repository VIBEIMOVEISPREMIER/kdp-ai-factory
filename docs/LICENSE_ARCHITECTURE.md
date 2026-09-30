# Arquitetura pública e privada de licenciamento

O KDP AI Factory mantém o aplicativo/editorial como código aberto e separa a infraestrutura oficial de confiança.

## Repositório público

O repositório público contém:

- criação e edição de livros;
- dashboard;
- importação e exportação;
- validação KDP;
- IA local/opcional;
- cliente de licenciamento;
- cálculo do Machine ID;
- chave pública para verificar licenças;
- contratos HTTP do serviço oficial;
- documentação.

O aplicativo público nunca deve conter:

- chave privada de assinatura;
- Bybit API key;
- Bybit API secret;
- credenciais do banco de produção;
- segredos do ambiente oficial.

## Repositório privado

A implementação oficial do servidor de licenças deve ficar em um repositório GitHub privado separado.

Ele será responsável por:

1. registrar máquinas;
2. controlar o consumo do livro gratuito;
3. verificar pagamentos;
4. impedir reutilização de TXID;
5. manter o banco de licenças;
6. vincular licença ao Machine ID;
7. assinar licenças com a chave privada;
8. responder às validações do aplicativo.

## Pagamento oficial

Parâmetros definidos pelo projeto:

- preço: US$ 50 vitalício;
- rede: BNB Smart Chain (BSC);
- ativos: USDT e BNB;
- carteira oficial: `0x09fa433f8df884356bbb8a1afe1fb11bea3e12e5`.

A validação deve conferir, no servidor:

- ativo;
- rede;
- endereço de destino;
- valor elegível;
- TXID;
- confirmações;
- unicidade da transação;
- vínculo entre pagamento, Machine ID e licença.

Para BNB, o servidor deve calcular o equivalente em USD usando uma cotação confiável no momento definido pela política de pagamento. Não deve assumir um valor fixo de BNB.

## Assinatura

A arquitetura usa criptografia assimétrica:

```text
SERVIDOR PRIVADO
    PRIVATE KEY
        |
        v
   licença assinada
        |
        v
APLICATIVO PÚBLICO
    PUBLIC KEY
        |
        v
verifica assinatura
```

A chave privada nunca é distribuída ao usuário.

## Trial remoto

Quando `KDP_LICENSE_SERVER_URL` estiver configurado, o servidor oficial será a autoridade para o limite de um livro.

O cliente chama:

```
POST /v1/trial/consume
{
  "machine_id": "...",
  "project_id": "..."
}
```

O `project_id` funciona como chave de idempotência para que uma tentativa repetida não consuma o mesmo trial duas vezes.

Quando o servidor não está configurado, o modo local/de desenvolvimento usa apenas o contador local.

## Limite do open source

Um fork pode remover ou modificar a própria tela de licença. Isso é uma característica inevitável do software aberto. O objetivo da arquitetura não é impedir forks, mas garantir que somente o servidor oficial emita licenças oficiais válidas para a distribuição oficial.

## Segredos

Use variáveis de ambiente/secret storage no servidor. Nunca faça commit de:

- `.env` de produção;
- chave privada;
- Bybit API key;
- Bybit API secret;
- banco de produção;
- tokens de clientes.
