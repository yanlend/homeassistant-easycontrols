"""
The binary sensor module for Helios Easy Controls integration.
"""
import logging

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_MAC
from homeassistant.helpers.entity import DeviceInfo, EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import HomeAssistantType

from custom_components.easycontrols import get_controller, get_device_info
from custom_components.easycontrols.const import (
    VARIABLE_BYPASS,
    VARIABLE_INFO_FILTER_CHANGE,
)
from custom_components.easycontrols.controller import Controller
from custom_components.easycontrols.modbus_variable import BoolModbusVariable

_LOGGER = logging.getLogger(__name__)


class EasyControlBinarySensor(BinarySensorEntity):
    """
    Represents a ModBus variable as a binary sensor.
    """

    def __init__(
        self,
        controller: Controller,
        variable: BoolModbusVariable,
        description: BinarySensorEntityDescription,
    ):
        """
        Initialize a new instance of `EasyControlsBinarySensor` class.

        Args:
            controller:
               The thread safe Helios Easy Controls controller.
            variable:
                The Modbus variable.
            description:
                The binary sensor description.
        """
        self.entity_description = description
        self._controller = controller
        self._variable = variable
        self._attr_unique_id = self._controller.mac + self.name

    async def async_update(self):
        """
        Updates the sensor value.
        """
        self._attr_is_on = await self._controller.get_variable(self._variable)
        self._attr_available = self._attr_is_on is not None

    @property
    def device_info(self) -> DeviceInfo:
        """
        Gets the device information.
        """
        return get_device_info(self._controller)


async def async_setup_entry(
    hass: HomeAssistantType,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    """
    Setup of Helios Easy Controls sensors for the specified config_entry.

    Args:
        hass:
            The Home Assistant instance.
        config_entry:
            The config entry which is used to create sensors.
        async_add_entities:
            The callback which can be used to add new entities to Home Assistant.

    Returns:
        The value indicates whether the setup succeeded.
    """
    _LOGGER.info("Setting up Helios EasyControls binary sensors.")

    controller = get_controller(hass, config_entry.data[CONF_MAC])

    async_add_entities(
        [
            EasyControlBinarySensor(
                controller,
                VARIABLE_BYPASS,
                BinarySensorEntityDescription(
                    key="bypass",
                    name=f"{controller.device_name} bypass",
                    icon="mdi:delta",
                    device_class=BinarySensorDeviceClass.OPENING,
                    entity_category=EntityCategory.DIAGNOSTIC,
                ),
            ),
            EasyControlBinarySensor(
                controller,
                VARIABLE_INFO_FILTER_CHANGE,
                BinarySensorEntityDescription(
                    key="filter_change",
                    name=f"{controller.device_name} filter change",
                    icon="mdi:air-filter",
                    device_class=BinarySensorDeviceClass.PROBLEM,
                    entity_category=EntityCategory.DIAGNOSTIC,
                ),
            ),
        ]
    )

    _LOGGER.info("Setting up Helios EasyControls binary sensors completed.")
