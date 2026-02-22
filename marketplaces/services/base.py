from abc import ABC, abstractmethod



class BaseMarketProducts(ABC):

    @abstractmethod
    def fetch_products(self):
        pass

    @abstractmethod
    def get_store_name(self):
        pass