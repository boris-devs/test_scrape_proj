from celery import shared_task
from celery.utils.log import get_task_logger

from marketplaces.services.dummyjson import DummyJsonMarketClient
from marketplaces.services.fakestoreapi import FakeStoreApiMarketClient
from marketplaces.sync import ServicesSynchronizer

logger = get_task_logger(__name__)

MARKET_CLIENTS = [
    FakeStoreApiMarketClient,
    DummyJsonMarketClient
]


@shared_task
def periodic_sync_markets():
    result = {"success": [], "failed": []}
    for client_class in MARKET_CLIENTS:
        client_name = client_class.__name__
        try:
            logger.info(f"Syncing marketplace: {client_name}")
            client = client_class()
            sync = ServicesSynchronizer(client)
            sync.sync_all()
            result["success"].append(client_name)
            logger.info(f"Synchronization completed for marketplace: {client_name}")
        except Exception as e:
            logger.error(f"Synchronization failed for marketplace: {client_name}: {e}", exc_info=True)
            result["failed"].append(client_name)
