import asyncio
import logging

_LOGGER = logging.getLogger(__name__)


class JtechRawClient:
    """Raw TCP client for a J Tech matrix on port 5000, using a persistent connection."""

    def __init__(self, host: str, port: int = 5000) -> None:
        self._host = host
        self._port = port
        self._reader: asyncio.StreamReader | None = None
        self._writer: asyncio.StreamWriter | None = None
        self._lock = asyncio.Lock()

    async def _ensure_connection(self) -> None:
        """Make sure there is an open TCP connection to the matrix."""
        if self._writer is not None and not self._writer.is_closing():
            return

        _LOGGER.info("Opening persistent TCP connection to J Tech matrix at %s:%s", self._host, self._port)

        try:
            self._reader, self._writer = await asyncio.open_connection(self._host, self._port)
        except Exception as err:
            _LOGGER.error("Failed to connect to J Tech matrix at %s:%s: %s", self._host, self._port, err)
            self._reader = None
            self._writer = None
            raise

    async def _send(self, command: str) -> None:
        """Send a raw command over the persistent connection."""
        full = command + "\r\n"

        async with self._lock:
            try:
                await self._ensure_connection()
            except Exception:
                return

            assert self._writer is not None

            _LOGGER.debug("Sending J Tech raw command to %s:%s: %r", self._host, self._port, full)

            try:
                self._writer.write(full.encode("ascii"))
                await self._writer.drain()
            except Exception as err:
                _LOGGER.error("Error sending command to J Tech matrix, dropping connection. Error %s", err)
                try:
                    self._writer.close()
                    await self._writer.wait_closed()
                except Exception:
                    pass
                self._reader = None
                self._writer = None

    async def async_set_route(self, output_1_based: int, input_1_based: int) -> None:
        """Route input to output using zero based values."""
        out_zero = output_1_based - 1
        in_zero = input_1_based - 1
        cmd = f"#video_d out{out_zero} source={in_zero}"

        _LOGGER.info(
            "J Tech route. Output %s Input %s Zero based %s Command %r",
            output_1_based,
            input_1_based,
            (out_zero, in_zero),
            cmd,
        )

        await self._send(cmd)

    async def async_set_route_all(self, input_1_based: int) -> None:
        """Route one input to all outputs using zero based."""
        in_zero = input_1_based - 1
        cmd = f"#video_d out255 source={in_zero}"

        _LOGGER.info(
            "J Tech route all. Input %s Zero based %s Command %r",
            input_1_based,
            in_zero,
            cmd,
        )

        await self._send(cmd)
