from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.media_player import (
    MediaPlayerEntity,
    MediaPlayerEntityFeature,
    MediaPlayerDeviceClass,
)
from homeassistant.components.media_player.const import MediaPlayerEntityFeature as MPFeature
from homeassistant.const import STATE_ON
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry

from .const import (
    DOMAIN,
    ATTR_MANUFACTURER,
    CONF_INPUTS,
    CONF_OUTPUTS,
)
from .raw_client import JtechRawClient

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up J-Tech matrix media players from config entry."""

    host: str = entry.data["host"]
    port: int = entry.data["port"]
    inputs: int = entry.data[CONF_INPUTS]
    outputs: int = entry.data[CONF_OUTPUTS]

    client = JtechRawClient(host, port)

    entities: list[JtechMatrixOutputEntity] = []

    for output_index in range(1, outputs + 1):
        entities.append(
            JtechMatrixOutputEntity(
                entry=entry,
                client=client,
                output_index=output_index,
                inputs=inputs,
            )
        )

    async_add_entities(entities)


class JtechMatrixOutputEntity(MediaPlayerEntity):
    """Representation of one matrix output as a media player."""

    _attr_device_class = MediaPlayerDeviceClass.TV
    _attr_has_entity_name = True
    _attr_icon = "mdi:video-input-hdmi"

    def __init__(
        self,
        entry: ConfigEntry,
        client: JtechRawClient,
        output_index: int,
        inputs: int,
    ) -> None:
        self._entry = entry
        self._client = client
        self._output_index = output_index
        self._inputs = inputs
        self._current_input: int | None = None

        self._attr_name = f"Output {output_index}"
        self._attr_unique_id = f"{entry.entry_id}_output_{output_index}"
        self._attr_supported_features = MPFeature.SELECT_SOURCE

    @property
    def device_info(self) -> DeviceInfo:
        """Return device info so all outputs group under one device."""
        host = self._entry.data["host"]
        return DeviceInfo(
            identifiers={(DOMAIN, self._entry.entry_id)},
            name=f"J-Tech Matrix ({host})",
            manufacturer=ATTR_MANUFACTURER,
            model="Raw TCP Matrix",
            configuration_url=f"http://{host}",
        )

    @property
    def state(self) -> str:
        """Return a simple state.

        We do not have real feedback over raw TCP, so treat as on if configured.
        """
        return STATE_ON

    @property
    def source_list(self) -> list[str]:
        """Return available input names."""
        return [f"Input {i}" for i in range(1, self._inputs + 1)]

    @property
    def source(self) -> str | None:
        """Return the current input name if known."""
        if self._current_input is None:
            return None
        return f"Input {self._current_input}"

    async def async_select_source(self, source: str) -> None:
        """Select input source for this output."""
        try:
            # Source will be like "Input 3"
            parts = source.strip().split()
            input_num = int(parts[-1])
        except Exception:
            _LOGGER.warning("Invalid source name %r for J Tech matrix", source)
            return

        _LOGGER.info(
            "J Tech matrix entity %s routing input %s to output %s",
            self._attr_name,
            input_num,
            self._output_index,
        )

        # Call the raw TCP client
        await self._client.async_set_route(self._output_index, input_num)

        # Remember state for UI
        self._current_input = input_num
        self.async_write_ha_state()

