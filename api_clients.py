# api_clients.py

import aiohttp
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from utils import logger
import json
import config

class APIClient:
    """Базовый класс для выполнения HTTP-запросов."""

    @staticmethod
    async def fetch(session: aiohttp.ClientSession, method: str, url: str, **kwargs) -> Optional[Any]:
        try:
            async with session.request(method, url, **kwargs) as response:
                response.raise_for_status()
                content_type = response.headers.get('Content-Type', '')
                if 'application/json' in content_type:
                    return await response.json()
                else:
                    return await response.text()
        except aiohttp.ClientError as e:
            logger.error(f"HTTP request failed: {e}")
            return None

class GetGemsClient(APIClient):
    """Клиент для взаимодействия с API GetGems."""

    async def fetch_nft_data(self, session: aiohttp.ClientSession) -> Dict[str, Any]:
        params = {
            "query": """
            query nftSearch {
              alphaNftItemSearch(
                query: "{\\"$and\\":[{\\"collectionAddress\\":\\"EQAOQdwdw8kGftJCSFgOErM1mBjYPe4DBPq8-AhF6vr9si5N\\"},{\\"saleType\\":\\"fix_price\\"}]}",
                sort: "[{\\"isOnSale\\":{\\"order\\":\\"desc\\"}},{\\"price\\":{\\"order\\":\\"asc\\"}},{\\"index\\":{\\"order\\":\\"asc\\"}}]",
                first: 1
              ) {
                edges {
                  node {
                    address
                    sale {
                      ... on NftSaleFixPrice {
                        fullPrice
                      }
                      ... on NftSaleFixPriceDisintar {
                        fullPrice
                      }
                    }
                  }
                }
              }
            }
            """,
            "variables": {},
        }
        headers = {"Accept": "application/json"}

        data = await self.fetch(session, 'POST', config.GETGEMS_URL, json=params, headers=headers)
        result_data = {}

        if data and "data" in data and "alphaNftItemSearch" in data["data"]:
            edges = data["data"]["alphaNftItemSearch"].get("edges", [])
            if edges:
                node = edges[0].get("node", {})
                address = node.get("address")
                sale_data = node.get("sale", {})
                full_price_str = sale_data.get("fullPrice")
                if full_price_str:
                    try:
                        full_price = int(full_price_str) / 1e9 + 0.3
                        result_data = {
                            "link_getgems": f"https://getgems.io/collection/EQAOQdwdw8kGftJCSFgOErM1mBjYPe4DBPq8-AhF6vr9si5N/{address}?modalNft={address}&modalId=nft_buy",
                            "price_getgems_ton": round(full_price, 2),
                        }
                    except ValueError:
                        logger.error("Failed to convert fullPrice to integer")
                else:
                    logger.error("fullPrice not found in sale data")
            else:
                logger.error("No edges found in GetGems response")
        else:
            logger.error("Invalid data format in GetGems response")
        return result_data

class PriceClient(APIClient):
    """Клиент для получения цены TON."""

    async def fetch_price_ton(self, session: aiohttp.ClientSession) -> Optional[float]:
        headers = {"Accept": "application/json"}
        data = await self.fetch(session, 'GET', config.PRICE_TON_URL, headers=headers)
        if data:
            try:
                price = data["data"]["attributes"]["token_prices"]["EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c"]
                return round(float(price), 2)
            except (KeyError, ValueError) as e:
                logger.error(f"Error parsing TON price: {e}")
        return None

class StonfiClient(APIClient):
    """Клиент для взаимодействия с API Ston.fi."""

    async def fetch_stonfi_data(self, session: aiohttp.ClientSession) -> Optional[float]:
        url = f"{config.STONFI_BASE_URL}/reverse_swap/simulate"
        params = {
            "offer_address": "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c",
            "ask_address": "EQC1bH4tFR2tEVQuW4i2RwwpccoaSy-GRQEqYrCKgZNfNw0r",
            "units": "1000000000000000",
            "slippage_tolerance": "1",
        }
        headers = {"Accept": "application/json"}

        data = await self.fetch(session, 'POST', url, params=params, headers=headers, data="")
        if data:
            try:
                offer_units = data["offer_units"]
                price_8num_ton = round(int(offer_units) / 1e9, 2) + 0.5
                return price_8num_ton
            except (KeyError, ValueError) as e:
                logger.error(f"Error parsing Ston.fi data: {e}")
        return None

    async def fetch_stonfi_sale_data(self, session: aiohttp.ClientSession) -> Optional[float]:
        url = f"{config.STONFI_BASE_URL}/swap/simulate"
        params = {
            "offer_address": "EQC1bH4tFR2tEVQuW4i2RwwpccoaSy-GRQEqYrCKgZNfNw0r",
            "ask_address": "EQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM9c",
            "units": "1000000000000000",
            "slippage_tolerance": "1",
        }
        headers = {"Accept": "application/json"}

        data = await self.fetch(session, 'POST', url, params=params, headers=headers, data="")
        if data:
            try:
                ask_units = data["ask_units"]
                price_8num_ton_sale = round(int(ask_units) / 1e9, 2) + 0.5
                return price_8num_ton_sale
            except (KeyError, ValueError) as e:
                logger.error(f"Error parsing Ston.fi sale data: {e}")
        return None

class FragmentClient(APIClient):
    """Клиент для парсинга данных с сайта Fragment."""

    async def fetch_and_parse_fragment(self, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "text/html",
        }
        html = await self.fetch(session, 'GET', config.FRAGMENT_URL, headers=headers)
        if html:
            return self.parse_page(html)
        else:
            logger.error("Failed to fetch or parse Fragment page")
        return None

    @staticmethod
    def parse_page(html: str) -> Optional[Dict[str, Any]]:
        soup = BeautifulSoup(html, "html.parser")
        first_row = soup.find("tr", class_="tm-row-selectable")
        if first_row:
            link = first_row.find("a", class_="table-cell")["href"]
            link_fragment = "https://fragment.com" + link
            price_fragment_ton = first_row.find(
                "div", class_="table-cell-value tm-value icon-before icon-ton"
            ).text.strip()
            return {
                "link_fragment": link_fragment,
                "price_fragment_ton": float(price_fragment_ton),
            }
        return None


class XRareClient:
    """Client for interacting with XRare API."""

    async def fetch_nft_data(self, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        headers = {"Accept": "application/json", "Content-Type": "application/json"}
        try:
            async with session.post(config.XRARE_URL, json=config.XRARE_PAYLOAD, headers=headers) as response:
                response.raise_for_status()
                data = await response.json()

                # Check if data contains NFTs and the first item has the expected fields
                if data.get("ok") and "nfts" in data and data["nfts"]:
                    nft = data["nfts"][0]
                    address = nft.get("address")
                    ton_price = nft.get("ton_price")
                    if address and ton_price:
                        # Create the buy link and prepare the result dictionary
                        return {
                            "xrare_price_ton": ton_price,
                            "xrare_link": f"https://xrare.io/nft/{address}/buy"
                        }
                else:
                    logger.error("No NFTs found or invalid response format from XRare API")
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching data from XRare API: {e}")
        return None
    

class MarketAppClient:
    """Client for scraping data from MarketApp collection page."""

    async def fetch_nft_data(self, session: aiohttp.ClientSession) -> Optional[Dict[str, Any]]:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Accept": "text/html",
        }
        try:
            async with session.get(config.MARKETAPP_COLLECTION_URL, headers=headers) as response:
                response.raise_for_status()
                html = await response.text()

                # Parse the HTML
                soup = BeautifulSoup(html, "html.parser")

                # Find the first element with the "tm-row-selectable" class
                row = soup.find("tr", class_="tm-row-selectable")
                if row:
                    # Extract the NFT link
                    nft_link = row.find("a", class_="table-cell")["href"]
                    full_link = f"https://marketapp.ws{nft_link}"

                    # Extract the price in TON
                    price_ton_text = row.find("div", class_="table-cell-value tm-value icon-before icon-ton").text.strip()
                    try:
                        price_ton = float(price_ton_text.replace(",", ""))
                    except ValueError:
                        logger.error("Failed to convert MarketApp price to float")
                        return None

                    return {
                        "marketapp_price_ton": price_ton,
                        "marketapp_link": full_link
                    }
                else:
                    logger.error("No selectable row found on MarketApp page")
        except aiohttp.ClientError as e:
            logger.error(f"Error fetching data from MarketApp: {e}")
        return None