# config.py

# URL-адреса API
GETGEMS_URL = "https://api.getgems.io/graphql"
PRICE_TON_URL = "https://api.geckoterminal.com/api/v2/simple/networks/ton/token_price/EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c"
STONFI_BASE_URL = "https://api.ston.fi/v1"
FRAGMENT_URL = "https://fragment.com/numbers?sort=price_asc&filter=sale"

# Комиссии
COMMISSION_GETGEMS_SALE = 0.05  # 5% комиссия для GetGems
COMMISSION_FRAGMENT_SALE = 0.05  # 5% комиссия для Fragment
MARKETAPP_COMMISSION_SALE = 0.01 #1% комиссия для MarketApp
TOTAL_COMMISSION_SALE = COMMISSION_GETGEMS_SALE + COMMISSION_FRAGMENT_SALE


# Другие настройки
SLEEP_INTERVAL = 8  # Интервал между запросами в секундах

# URL for XRare API
XRARE_URL = "https://api.xrare.io/api/v1/nfts"

# Default payload for XRare API request
XRARE_PAYLOAD = {
    "address": "EQAOQdwdw8kGftJCSFgOErM1mBjYPe4DBPq8-AhF6vr9si5N",
    "atts": [],
    "currency": "TON",
    "cursor": "",
    "fromPrice": "",
    "model": "collection",
    "sale": "",
    "search": "",
    "sort": "price_low",
    "toPrice": "",
}

# URL for MarketApp collection page
MARKETAPP_COLLECTION_URL = "https://marketapp.ws/collection/EQAOQdwdw8kGftJCSFgOErM1mBjYPe4DBPq8-AhF6vr9si5N/"
