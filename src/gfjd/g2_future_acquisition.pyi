from collections.abc import Callable, Iterable, Mapping
from pathlib import Path
from typing import Protocol

class G2FutureAcquisitionError(RuntimeError): ...

class Response(Protocol):
    status: int
    headers: Mapping[str, str]
    def read(self, size: int = -1) -> bytes: ...
    def __enter__(self) -> Response: ...
    def __exit__(self, *args: object) -> object: ...

Transport = Callable[..., Response]
Resolver = Callable[[str, int], Iterable[str]]

def acquire_exact_url(
    *,
    url: str,
    exact_url_allowlist: Iterable[str],
    destination_root: Path,
    output_name: str,
    transport: Transport,
    resolver: Resolver | None = ...,
    max_redirects: int = ...,
    max_bytes: int = ...,
    timeout_seconds: float = ...,
    allowed_content_types: Iterable[str] = ...,
) -> tuple[dict[str, object], Path, Path]: ...
