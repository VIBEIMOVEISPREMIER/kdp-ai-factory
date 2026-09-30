# Deploy the license server on Render

The repository includes a Render service definition for the official license server.

## Required secrets

Configure these as Render secret environment variables:

- BYBIT_API_KEY
- BYBIT_API_SECRET
- KDP_LICENSE_PRIVATE_KEY_B64

Public configuration:

- KDP_PAYMENT_NETWORK=BSC
- KDP_PAYMENT_ADDRESS=0x09fa433f8df884356bbb8a1afe1fb11bea3e12e5
- KDP_PAYMENT_PRICE_USD=50
- BYBIT_BASE_URL=https://api.bybit.com

## Important

Do not put the Bybit secret or private signing key in GitHub. The Render service must use secret environment variables.

Before accepting real payments, complete the BSC secondary verification, transaction replay protection, database backup strategy, and end-to-end payment test.
