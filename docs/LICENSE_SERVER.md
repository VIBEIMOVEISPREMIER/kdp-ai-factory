# Official license service

The repository now contains the initial FastAPI service boundary under `apps/license_server/`.

## Trust model

The desktop application must never contain:

- a private signing key;
- exchange API secrets;
- production database credentials.

The official server will own those secrets and issue signed lifetime licenses after validating an eligible payment.

## Payment verification

The production adapter is designed around the exchange's on-chain deposit-record endpoint. The endpoint supports transaction-ID filtering and returns the coin, chain, amount, transaction ID, status, destination address and confirmations. The official documentation is:

https://bybit-exchange.github.io/docs/v5/asset/deposit/deposit-record

The final verifier must independently check:

1. supported asset;
2. BSC network;
3. exact destination wallet;
4. transaction uniqueness;
5. completed status and confirmation threshold;
6. minimum purchase value;
7. transaction-to-license binding.

Do not place exchange credentials in the desktop client or repository.

## Current status

The API boundary and service package are present. The production payment adapter and persistent license database are intentionally the next implementation step; do not treat the current endpoint as a completed payment processor.
