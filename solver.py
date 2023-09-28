import aiohttp
import asyncio
import difflib
import re

from bs4 import BeautifulSoup

from typing import Optional, Self


NewWordsResult = tuple[str, str, set[str]]


class Solver:
    def __init__(
        self,
        session: Optional[aiohttp.ClientSession] = None,
    ) -> None:
        self.session = session or aiohttp.ClientSession()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, *args) -> None:
        await self.session.close()

    _prefix = '/wiki/'
    async def get_new_words(
        self,
        word: str,
    ) -> NewWordsResult:
        # url = f'https://en.wikipedia.org/wiki/{word}'
        url = f'https://www.thewikigame.com/group/wiki/{word}'
        async with self.session.get(url) as response:
            html = await response.text()

        match = re.search(r'"wgPageName":"(.+?)"', html)
        if match is None:
            return (word, word, set())
        name = match.group(1)

        soup = BeautifulSoup(html, 'html.parser')
        links: list[Optional[str]] = [link.get('href') for link in soup.find_all('a')]
        words: set[str] = set(
            link.removeprefix(self._prefix) for link in links
            if link is not None
            and link.startswith(self._prefix)
            and ':' not in link
        )
        return (word, name, words)

    async def solve(
        self,
        start: str,
        end: str,
    ) -> None:
        start = start.replace(' ', '_')
        end = end.replace(' ', '_')
        lowered_end = end.lower()

        already_seen: set[str] = set()
        next_words: set[str] = set((start,))

        recent_paths: dict[str, list[str]] = {}
        actual_names: dict[str, str] = {}

        found: bool = False
        while not found:
            print('Searching...')
            # print(next_words)
            data: list[NewWordsResult] = await asyncio.gather(*(self.get_new_words(word) for word in next_words))
            next_words = set()

            for old, old_name, words in data:
                for word in words:
                    if word in already_seen:
                        continue
                    already_seen.add(word)
                    recent_paths[word] = recent_paths.get(old, []) + [word]
                    actual_names[old] = old_name
                    if word.lower() == lowered_end:
                        end = word
                        found = True
                        break
                    next_words.add(word)
                try:
                    recent_paths.pop(old)
                except KeyError:
                    pass
                if found:
                    break

            next_words = set(difflib.get_close_matches(
                end,
                next_words,
                n=25,
                cutoff=0.0,
            ))

        path = recent_paths[end]
        if path[0] != start:
            path.insert(0, start)

        print(' -> '.join(actual_names.get(word, word) for word in path))


async def main() -> None:
    async with Solver() as solver:
        await solver.solve(
            start='Fine art',
            end='Fruit',
        )


if __name__ == '__main__':
    asyncio.run(main())
