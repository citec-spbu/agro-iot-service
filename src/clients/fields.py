import logging
import uuid

from httpx import HTTPStatusError
from shapely.geometry import Point, Polygon, shape

from src.clients.base import BaseHttpClient
from src.config import settings

logger = logging.getLogger(__name__)


class FieldContoursClient(BaseHttpClient):
    async def get_field_contours(
        self, field_id: uuid.UUID, authorization: str
    ) -> list[dict]:
        headers = {
            "Content-Type": "application/json",
            "Authorization": authorization,
        }
        url = (
            f"{settings.GATEWAY_URL.rstrip('/')}"
            f"/api/fields-service/fields/{field_id}/contours"
        )
        try:
            response_json = await self.get_json(url, headers=headers)
        except HTTPStatusError as exc:
            raise self.to_runtime_error(exc, "field contours") from exc
        if not isinstance(response_json, list):
            raise RuntimeError("field contours: expected JSON array")
        return response_json

    async def point_in_field(
        self,
        field_id: uuid.UUID,
        latitude: float,
        longitude: float,
        authorization: str,
    ) -> bool | None:
        """Возвращает True/False если контуры доступны, None если проверить нельзя."""
        try:
            contours = await self.get_field_contours(field_id, authorization)
        except Exception as exc:
            logger.warning("Skipping point-in-polygon check: %s", exc)
            return None

        point = Point(longitude, latitude)
        for contour in contours:
            polygon = self._extract_polygon(contour)
            if polygon is None:
                continue
            if polygon.contains(point):
                return True
        return False

    @staticmethod
    def _extract_polygon(contour: dict) -> Polygon | None:
        # GeoJSON-style {"type":"Polygon","coordinates":[[[lon,lat],...]]}
        geom = contour.get("geom") or contour.get("geometry")
        if geom:
            try:
                return shape(geom)
            except (ValueError, TypeError) as exc:
                logger.warning("Bad GeoJSON contour: %s", exc)
                return None
        # fields-service style: contour["coordinates"] = [{"longitude":..,"latitude":..}, ...]
        coords = contour.get("coordinates")
        if isinstance(coords, list) and len(coords) >= 3:
            try:
                return Polygon(
                    [(c["longitude"], c["latitude"]) for c in coords]
                )
            except (KeyError, TypeError, ValueError) as exc:
                logger.warning("Bad coordinates list: %s", exc)
        return None
