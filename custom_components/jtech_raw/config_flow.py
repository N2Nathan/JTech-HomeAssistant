from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow
from homeassistant.const import CONF_HOST, CONF_PORT
from homeassistant.data_entry_flow import FlowResult

from .const import (
    DOMAIN,
    CONF_INPUTS,
    CONF_OUTPUTS,
    DEFAULT_PORT,
    DEFAULT_INPUTS,
    DEFAULT_OUTPUTS,
)


class JtechRawMatrixConfigFlow(ConfigFlow, domain=DOMAIN):
    """Config flow for J-Tech Raw Matrix."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            host = user_input[CONF_HOST]
            port = user_input[CONF_PORT]

            # Use host+port as unique id to avoid duplicates
            await self.async_set_unique_id(f"{DOMAIN}_{host}_{port}")
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=f"J-Tech Matrix ({host})",
                data=user_input,
            )

        if user_input is None:
            user_input = {
                CONF_HOST: "",
                CONF_PORT: DEFAULT_PORT,
                CONF_INPUTS: DEFAULT_INPUTS,
                CONF_OUTPUTS: DEFAULT_OUTPUTS,
            }

        schema = vol.Schema(
            {
                vol.Required(CONF_HOST, default=user_input.get(CONF_HOST, "")): str,
                vol.Required(CONF_PORT, default=user_input.get(CONF_PORT, DEFAULT_PORT)): int,
                vol.Required(
                    CONF_INPUTS,
                    default=user_input.get(CONF_INPUTS, DEFAULT_INPUTS),
                ): vol.All(int, vol.Range(min=1, max=32)),
                vol.Required(
                    CONF_OUTPUTS,
                    default=user_input.get(CONF_OUTPUTS, DEFAULT_OUTPUTS),
                ): vol.All(int, vol.Range(min=1, max=32)),
            }
        )

        return self.async_show_form(step_id="user", data_schema=schema, errors=errors)
