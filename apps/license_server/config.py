import os

PAYMENT_NETWORK = os.getenv('KDP_PAYMENT_NETWORK', 'BSC')
PAYMENT_ADDRESS = os.getenv('KDP_PAYMENT_ADDRESS', '0x09fa433f8df884356bbb8a1afe1fb11bea3e12e5')
PAYMENT_PRICE_USD = float(os.getenv('KDP_PAYMENT_PRICE_USD', '50'))
BYBIT_BASE_URL = os.getenv('BYBIT_BASE_URL', 'https://api.bybit.com')
DATABASE_URL = os.getenv('KDP_LICENSE_DATABASE_URL', 'sqlite:///data/license_server.sqlite3')
