import httpx

from marketplaces.services.base import BaseMarketProducts


class FakeStoreApiMarketClient(BaseMarketProducts):
    url = "https://fakestoreapi.com/products"
    store_name = "FakeStoreAPI"
    def fetch_products(self):
        all_products = httpx.get(self.url)
        json = all_products.json()
        return json

    @classmethod
    def get_store_name(cls):
        return cls.store_name