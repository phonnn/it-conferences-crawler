import aiohttp


async def fetch(url, headers=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, headers=headers) as response:
            if response.status == 200:
                content_type = response.headers.get('Content-Type', '').lower()
                if 'application/json' in content_type:
                    return await response.json()
                elif 'text/html' in content_type:
                    return await response.text()
                else:
                    return await response.read()
            raise Exception(f"Failed to fetch {url}: Status code {response.status}")


def safe_int(value, default=None):
    try:
        return int(value)
    except (ValueError, TypeError):
        return default