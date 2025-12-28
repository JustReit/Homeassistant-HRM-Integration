from __future__ import annotations

import logging
from typing import Optional

from bleak import BleakClient
from bleak_retry_connector import establish_connection
from habluetooth import HaBleakClientWrapper


from homeassistant.components.sensor import SensorEntity
from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_MAC, HR_CHAR_UUID

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities,
):
    async_add_entities(
        [HeartRateSensor(hass, entry.data[CONF_MAC], entry.entry_id)]
    )


class HeartRateSensor(SensorEntity):
    _attr_icon = "mdi:heart"
    _attr_unit_of_measurement = "bpm"
    _attr_should_poll = False

    def __init__(self, hass: HomeAssistant, mac: str, entry_id: str):
        self.hass = hass
        self.mac = mac
        self._attr_name = f"Heart Rate {mac[-5:]}"
        self._attr_unique_id = f"{entry_id}_heart_rate"
        self._attr_native_value: Optional[int] = None

        self._client: Optional[BleakClient] = None
        self._connecting = False

    async def async_added_to_hass(self):
        # IMPORTANT: never block entity setup
        self.hass.async_create_task(self._connect_and_subscribe())

    async def _connect_and_subscribe(self):
        if self._connecting:
            return

        self._connecting = True

        device = async_ble_device_from_address(
            self.hass, self.mac, connectable=True
        )

        if not device:
            _LOGGER.error("BLE device %s not found via ESP BLE Proxy", self.mac)
            self._connecting = False
            return

        try:
            _LOGGER.debug("Connecting to HRM %s", self.mac)

            self._client = await establish_connection(
                HABleakClientWrapper,
                device,
                self.mac,
                timeout=30.0,
            )

            await self._client.start_notify(
                HR_CHAR_UUID, self._notification_handler
            )

            _LOGGER.info("Connected to HRM %s", self.mac)
            self.schedule_update_ha_state()

        except Exception as err:
            _LOGGER.warning(
                "Failed to connect to HRM %s: %s", self.mac, err
            )

        finally:
            self._connecting = False

    def _notification_handler(self, _: int, data: bytearray):
        """
        Bluetooth SIG Heart Rate Measurement parsing
        Matches ESPHome lambda exactly:
          uint16_t hr = x[1];
          if (x[0] & 0x01) hr |= x[2] << 8;
        """
        if not data or len(data) < 2:
            return

        flags = data[0]
        hr = data[1]

        if flags & 0x01 and len(data) >= 3:
            hr |= data[2] << 8

        self._attr_native_value = hr
        self.schedule_update_ha_state()

    @property
    def available(self) -> bool:
        return self._client is not None and self._client.is_connected

    async def async_will_remove_from_hass(self):
        if self._client and self._client.is_connected:
            await self._client.disconnect()

