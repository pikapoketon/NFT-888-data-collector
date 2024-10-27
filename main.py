# main.py

import asyncio
from data_aggregator import DataAggregator
from utils import setup_logging


def main():
    setup_logging()
    aggregator = DataAggregator()
    asyncio.run(aggregator.aggregate_data())


if __name__ == "__main__":
    main()
