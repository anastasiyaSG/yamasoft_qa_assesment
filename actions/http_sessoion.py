import aiohttp


@pytest.fixture()
async def http_session():
    """Fixture to create a new HTTP session for each test."""
    async with aiohttp.ClientSession() as session:
        yield session