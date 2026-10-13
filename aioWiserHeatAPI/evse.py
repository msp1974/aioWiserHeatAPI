"""Support for Wiser EV charging socket equipment."""

from .const import TEXT_UNKNOWN, WISEREQUIPMENT
from .helpers.device import _WiserDevice
from .helpers.equipment import _WiserEquipment


class _WiserEVSE(_WiserDevice):
    """A Wiser EVSE represented by a Device and an Equipment record."""

    @property
    def equipment(self) -> _WiserEquipment:
        """Return the EVSE equipment data."""
        return _WiserEquipment(self._device_type_data)

    @property
    def equipment_id(self) -> int:
        """Return the equipment record id."""
        return self.equipment.id

    @property
    def instantaneous_power(self) -> int | None:
        """Return current active power in watts."""
        power = self.equipment.power
        return (
            power.total_active_power
            if power.total_active_power is not None
            else power.active_power
        )

    @property
    def delivered_power(self) -> int | None:
        """Return accumulated delivered energy in watt-hours."""
        return self.equipment.power.current_summation_delivered

    @property
    def available_control_states(self) -> list[str]:
        """Return control states accepted by the hub for this equipment."""
        return self._device_type_data.get("AvailableControlState", [])

    @property
    def control_state(self) -> str:
        """Return the current load control state."""
        return self._device_type_data.get(
            "ControlState",
            self._device_type_data.get(
                "LoadStateCommandPrio",
                self._device_type_data.get("LoadStateStatus", TEXT_UNKNOWN),
            ),
        )

    @property
    def is_on(self) -> bool:
        """Return whether charging has not been force-disabled."""
        return self.control_state not in {"consumptionForceOff", "Off"}

    async def _set_control_state(self, state: str) -> bool:
        """Set one of the control states advertised by the equipment."""
        if state not in self.available_control_states:
            raise ValueError(
                f"{state} is not a valid EVSE control state. "
                f"Valid states are {self.available_control_states}"
            )

        result = await self._wiser_rest_controller._send_command(
            WISEREQUIPMENT.format(self.equipment_id), {"ControlState": state}
        )
        if result:
            # Some hub versions return only the changed field. Preserve the
            # equipment telemetry and advertised states until the next poll.
            self._device_type_data = {**self._device_type_data, **result}
            return True
        return False

    async def turn_on(self) -> bool:
        """Return the EVSE to its normal self-managed state."""
        return await self._set_control_state("selfManagement")

    async def turn_off(self) -> bool:
        """Force EVSE consumption off."""
        return await self._set_control_state("consumptionForceOff")


class _WiserEVSECollection:
    """Collection of Wiser EV charging socket devices."""

    def __init__(self):
        self._items = []

    @property
    def all(self) -> list[_WiserEVSE]:
        """Return all EVSE devices."""
        return list(self._items)

    @property
    def count(self) -> int:
        """Return the number of EVSE devices."""
        return len(self.all)

    def get_by_id(self, device_id: int) -> _WiserEVSE | None:
        """Return an EVSE by its physical device id."""
        return next((device for device in self.all if device.id == device_id), None)
