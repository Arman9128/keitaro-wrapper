import httpx

from app.core.config import settings


class KeitaroClient:
    def __init__(self):
        self.base_url = settings.keitaro_base_url.rstrip("/")
        self.api_key = settings.keitaro_api_key

    def _get_headers(self):
        if not self.api_key:
            raise ValueError("Keitaro API key is not configured")

        return {
            "Api-Key": self.api_key,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

    async def get(self, endpoint: str):
        url = f"{self.base_url}/admin_api/v1/{endpoint.lstrip('/')}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                url,
                headers=self._get_headers(),
            )
            response.raise_for_status()
            return response.json()

    async def post(self, endpoint: str, data: dict):
        url = f"{self.base_url}/admin_api/v1/{endpoint.lstrip('/')}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                url,
                headers=self._get_headers(),
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def put(self, endpoint: str, data: dict):
        url = f"{self.base_url}/admin_api/v1/{endpoint.lstrip('/')}"

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.put(
                url,
                headers=self._get_headers(),
                json=data,
            )
            response.raise_for_status()
            return response.json()

    async def check_connection(self):
        return await self.get("campaigns")
