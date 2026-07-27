import httpx

from app.config import settings

class PolzaClient:
    def __init__(self)-> None:
        self.client = httpx.AsyncClient(
            base_url=settings.polza_api_base_url,
            timeout=settings.polza_timeount_seconds
        )

    async def close(self) -> None:
        await self.client.aclose()

    def headers(self) -> dict[str, str]:
        return { "Authorization": f"Bearer {settings.polza_api_key}"}     

    async def list_models(self) -> list[dict[str, str]]:
        pass

    async def complete(self, model_id: str, messages: list[dict[str, str]]) -> str:
        pass

    async def _request(self, method: str, path: str, **kwargs: Any):
        try:
            response = await self.client.request(
                method, path, headers=self.headers(), **kwargs
            )
        except httpx.TimeoutException as exc:
            raise PolzaError("Polza.ai не ответил за отведенное время") from exc
        except httpx.HTTPError as exc:
            raise PolzaError("Не удалось подключится к Polza.ai") from exc

        if response.is_success:
            return response

        try:
            message = response.json().get("error", {}).get("message")
        except (AttributeError, ValueError):
            message = None
            raise PolzaError(message or "Polza.ai вернул ошибку")