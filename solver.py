import aiohttp
import asyncio
import random

from bs4 import BeautifulSoup

from typing import Optional


class Solver:
    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self.session = session or aiohttp.ClientSession()

    _prefix = '/wiki/'
    async def get_new_words(
        self,
        word: str,
    ) -> list[str]:
        async with self.session.get(
            f'https://en.wikipedia.org/wiki/{word}',
        ) as response:
            html = await response.text()
        soup = BeautifulSoup(html, 'html.parser')
        links: list[Optional[str]] = [link.get('href') for link in soup.find_all('a')]
        words: list[str] = [
            link.removeprefix(self._prefix) for link in links
            if link is not None
            and link.startswith(self._prefix)
            and ':' not in link
        ]
        return words

    async def solve(
        self,
        start: str,
        end: str,
    ) -> None:
        start = start.replace(' ', '_')
        end = end.replace(' ', '_')

        already_seen: set[str] = set()
        next_words: list[str] = [start]

        recent_paths: dict[str, list[str]] = {}

        found: bool = False
        while not found:
            data = await asyncio.gather(*(self.get_new_words(word) for word in next_words))
        print(recent_paths[end])
        print('Found!')


async def main() -> None:
    solver = Solver()
    await solver.solve(
        start='Great Depression',
        end='Europe',
    )


if __name__ == '__main__':
    asyncio.run(main())
