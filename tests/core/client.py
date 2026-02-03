import io
import json
import tempfile

from pathlib import Path
from typing import (
    Any,
    Dict,
    Optional,
    Protocol,
    Union,
)
from urllib.parse import urlencode

from PIL import Image

from qgis.core import QgsProject
from qgis.server import QgsBufferServerResponse


class Response:
    def __init__(self, resp: QgsBufferServerResponse) -> None:
        self._resp = resp
        self._json = None

    def json(self) -> Any:
        if self._json is None and self._resp.headers().get('Content-Type','').find('application/json')==0:
            self._json = json.loads(self.content.decode('utf-8'))
        return self._json

    @property
    def content(self) -> bytes:
        return bytes(self._resp.body())

    @property
    def status_code(self) -> int:
        return self._resp.statusCode()

    @property
    def headers(self) -> Dict[str,str]:
        return self._resp.headers()


class Client(Protocol):
    @property
    def plugin(self) -> Any: ...
    def get_project_path(self, name: str) -> Path: ...
    def get_project(self, name: str) -> QgsProject: ...
    def get(
        self,
        query: str,
        project: Optional[str] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Response: ...
