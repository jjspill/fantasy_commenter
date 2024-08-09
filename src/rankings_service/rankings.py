from dataclasses import dataclass

import aiohttp


class RankingsScraper:
    def __init__(self, config_url: str):
        self.config_url = config_url

    async def fetch_data(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(self.config_url) as response:
                return await response.text()

    def extract_data(self, html_content):
        """Extract data from HTML content."""
        raise NotImplementedError

    def parse_data(self, raw_data):
        """Parse raw data into structured format."""
        raise NotImplementedError

    async def write_to_db(self, data):
        """Write data to a database."""
        raise NotImplementedError
