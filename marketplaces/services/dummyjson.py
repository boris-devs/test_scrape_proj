from marketplaces.services.base import BaseMarketProducts

import httpx


class DummyJsonMarketClient(BaseMarketProducts):
    url = "https://dummyjson.com/products"
    store_name = "DummyJSON"

    def fetch_products(self):
        limit = self.fetch_limit_per_page()
        all_products = httpx.get(self.url, params={"limit": limit})
        return all_products.json()

    def fetch_limit_per_page(self) -> int:
        page = httpx.get(self.url)
        limit = page.json()["limit"]
        return limit

    @classmethod
    def get_store_name(cls):
        return cls.store_name
