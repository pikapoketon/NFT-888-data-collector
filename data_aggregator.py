# data_aggregator.py

import asyncio
import aiohttp
from datetime import datetime
from typing import Dict, Any, Optional
import aiofiles
import json

from api_clients import GetGemsClient, PriceClient, StonfiClient, FragmentClient, XRareClient, MarketAppClient
from utils import logger
import config


class DataAggregator:
    def __init__(self):
        self.getgems_client = GetGemsClient()
        self.price_client = PriceClient()
        self.stonfi_client = StonfiClient()
        self.fragment_client = FragmentClient()
        self.xrare_client = XRareClient()
        self.marketapp_client = MarketAppClient()

    async def aggregate_data(self) -> None:
        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    tasks = [
                        self.getgems_client.fetch_nft_data(session),
                        self.price_client.fetch_price_ton(session),
                        self.stonfi_client.fetch_stonfi_data(session),
                        self.stonfi_client.fetch_stonfi_sale_data(session),
                        self.fragment_client.fetch_and_parse_fragment(session),
                        self.xrare_client.fetch_nft_data(session),
                        self.marketapp_client.fetch_nft_data(session)
                    ]
                    results = await asyncio.gather(*tasks)

                    # Unpack results
                    nft_data, price_ton, price_8num_ton, price_8num_ton_sale, fragment_data, xrare_data, marketapp_data = results
                    combined_data = self.combine_data(
                        nft_data, price_ton, price_8num_ton, price_8num_ton_sale, fragment_data, xrare_data, marketapp_data
                    )

                    await self.save_data(combined_data)
                    logger.info("Data successfully saved to nft_data.json")

                await asyncio.sleep(config.SLEEP_INTERVAL)
            except Exception as e:
                logger.error(f"An error occurred in the main loop: {e}")

    @staticmethod
    def combine_data(
        nft_data: Dict[str, Any],
        price_ton: Optional[float],
        price_8num_ton: Optional[float],
        price_8num_ton_sale: Optional[float],
        fragment_data: Dict[str, Any],
        xrare_data: Dict[str, Any],
        marketapp_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        combined_data = {
            "getgems": {},
            "fragment": {},
            "xrare": {},
            "marketapp": {},
            "shardify": {},
            "general": {}
        }

        # Process GetGems data
        if nft_data:
            combined_data["getgems"].update({
                "link": nft_data.get("link_getgems"),
                "price_ton": nft_data.get("price_getgems_ton"),
                "price_ton_sale": round(nft_data["price_getgems_ton"] * (1 - config.TOTAL_COMMISSION_SALE), 2),
                "price_usdt": round(nft_data["price_getgems_ton"] * price_ton, 2) if price_ton else None,
                "price_usdt_sale": round(nft_data["price_getgems_ton"] * (1 - config.TOTAL_COMMISSION_SALE) * price_ton, 2) if price_ton else None
            })

        # Process Fragment data
        if fragment_data:
            combined_data["fragment"].update({
                "link": fragment_data.get("link_fragment"),
                "price_ton": fragment_data.get("price_fragment_ton"),
                "price_ton_sale": round(fragment_data["price_fragment_ton"] * (1 - config.COMMISSION_FRAGMENT_SALE), 2),
                "price_usdt": round(fragment_data["price_fragment_ton"] * price_ton, 2) if price_ton else None,
                "price_usdt_sale": round(fragment_data["price_fragment_ton"] * (1 - config.COMMISSION_FRAGMENT_SALE) * price_ton, 2) if price_ton else None
            })

        # Process XRare data
        if xrare_data:
            combined_data["xrare"].update({
                "link": xrare_data.get("xrare_link"),
                "price_ton": xrare_data.get("xrare_price_ton"),
                "price_ton_sale": xrare_data.get("xrare_price_ton"),  # Sale price is the same
                "price_usdt": round(xrare_data["xrare_price_ton"] * price_ton, 2) if price_ton else None,
                "price_usdt_sale": round(xrare_data["xrare_price_ton"] * price_ton, 2) if price_ton else None
            })

        # Process MarketApp data with 1% commission
        if marketapp_data:
            marketapp_sale_price_ton = marketapp_data["marketapp_price_ton"] * (1 - config.MARKETAPP_COMMISSION_SALE)
            combined_data["marketapp"].update({
                "link": marketapp_data.get("marketapp_link"),
                "price_ton": marketapp_data.get("marketapp_price_ton"),
                "price_ton_sale": round(marketapp_sale_price_ton, 2),
                "price_usdt": round(marketapp_data["marketapp_price_ton"] * price_ton, 2) if price_ton else None,
                "price_usdt_sale": round(marketapp_sale_price_ton * price_ton, 2) if price_ton else None
            })

        # Process shardify data
        if price_8num_ton and price_8num_ton_sale:
            combined_data["shardify"].update({
                "price_ton": price_8num_ton,
                "price_ton_sale": price_8num_ton_sale,
                "price_usdt": round(price_8num_ton * price_ton, 2) if price_ton else None,
                "price_usdt_sale": round(price_8num_ton_sale * price_ton, 2) if price_ton else None
            })

        # Add general data
        combined_data["general"].update({
            "price_ton": price_ton,
            "last_update": datetime.now().isoformat(),
            "commissions": {
                "getgems_sale": config.COMMISSION_GETGEMS_SALE,
                "fragment_sale": config.COMMISSION_FRAGMENT_SALE,
                "marketapp_sale": config.MARKETAPP_COMMISSION_SALE
            }
        })

        return combined_data

    @staticmethod
    async def save_data(data: Dict[str, Any]) -> None:
        async with aiofiles.open("nft_data.json", "w", encoding="utf-8") as json_file:
            await json_file.write(json.dumps(data, ensure_ascii=False, indent=4))