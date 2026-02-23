from marketplaces.services.base import BaseMarketProducts

import httpx


class DummyJsonMarketClient(BaseMarketProducts):
    BASE_URL = "https://dummyjson.com/products"
    STORE_NAME = "DummyJSON"

    def fetch_products(self):
        """Fetch all products from DummyJSON API."""
        total = self.total_products_count()
        params = {"limit": total} if total else {}
        response = httpx.get(self.BASE_URL, params=params)
        response.raise_for_status()
        data = response.json()
        return data["products"]


    def total_products_count(self) -> int | None:
        response = httpx.get(self.BASE_URL)
        return response.json().get("total", None)

    @classmethod
    def get_store_name(cls):
        return cls.STORE_NAME
