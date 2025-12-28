from __future__ import annotations

from bleak import BleakClient

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.bluetooth import async_ble_device_from_address
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, CONF_MAC, HR_CHAR_UUID


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

    def __init__(self, hass, mac, entry_id):
        self.hass = hass
        self.mac = mac
        self._attr_name = f"Heart Rate {mac[-5:]}"
        self._attr_unique_id = f"{entry_id}_heart_rate"
        self._attr_native_value = None
        self._client: BleakClient | None = None

    async def async_added_to_hass(self):
        device = async_ble_device_from_address(
            self.hass, self.mac, connectable=True
        )

        if not device:
            raise RuntimeError("BLE device not found via ESP BLE Proxy")

        self._client = BleakClient(device)
        await self._client.connect()

        await self._client.start_notify(
            HR_CHAR_UUID, self._notification_handler
        )

    def _notification_handler(self, _: int, data: bytearray):
        flags = data[0]
        hr = data[1]

        if flags & 0x01:
            hr |= data[2] << 8

        self._attr_native_value = hr
        self.schedule_update_ha_state()

    async def async_will_remove_from_hass(self):
        if self._client and self._client.is_connected:
            await self._client.disconnect()
