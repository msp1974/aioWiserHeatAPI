from ..const import WISERHUBOPENTHERM
from ..rest_controller import WiserRestActionEnum, _WiserRestController
from .temp import _WiserTemperatureFunctions as tf


class _WiserOpenThermBoilerParameters:
    """Data structure for Opentherm Boiler Parameters data"""

    def __init__(self, data: dict):
        self._data = data

    @property
    def ch_max_setpoint_read_write(self) -> bool:
        return self._data.get("maxChSetpointReadWrite", None)

    @property
    def ch_max_setpoint_transfer_enable(self) -> bool:
        return self._data.get("maxChSetpointTransferEnable", None)

    @property
    def ch_setpoint(self) -> bool:
        return tf._from_wiser_temp(self._data.get("maxChSetpoint", None), "current")

    @property
    def ch_setpoint_lower_bound(self) -> bool:
        return tf._from_wiser_temp(
            self._data.get("maxChSetpointLowerBound", None), "current"
        )

    @property
    def ch_setpoint_upper_bound(self) -> bool:
        return tf._from_wiser_temp(
            self._data.get("maxChSetpointUpperBound", None), "current"
        )

    @property
    def hw_setpoint_read_write(self) -> bool:
        return self._data.get("dhwSetpointReadWrite", None)

    @property
    def hw_setpoint_transfer_enable(self) -> bool:
        return self._data.get("dhwSetpointTransferEnable", None)

    @property
    def hw_setpoint(self) -> bool:
        return tf._from_wiser_temp(self._data.get("dhwSetpoint", None), "current")

    @property
    def hw_setpoint_lower_bound(self) -> bool:
        return tf._from_wiser_temp(
            self._data.get("dhwSetpointLowerBound", None), "current"
        )

    @property
    def hw_setpoint_upper_bound(self) -> bool:
        return tf._from_wiser_temp(
            self._data.get("dhwSetpointUpperBound", None), "current"
        )

    @property
    def json_data(self) -> dict:
        return self._data


class _WiserOpenThermOperationalData:
    """Data structure for Opentherm Boiler Parameters data"""

    def __init__(self, data):
        self._data = data

    @property
    def ch_pressure_bar(self) -> str:
        """Get ChPressureBar"""
        return self._data.get("ChPressureBar", 0) / 10

    @property
    def ch_flow_temperature(self) -> str:
        """Get Ch1FlowTemperature"""
        return tf._from_wiser_temp(
            self._data.get("Ch1FlowTemperature", None), "current"
        )

    @property
    def ch_return_temperature(self) -> str:
        """Get ChReturnTemperature"""
        return tf._from_wiser_temp(
            self._data.get("ChReturnTemperature", None), "current"
        )

    @property
    def hw_flow_rate(self) -> str:
        """Get Dhw1Temperature"""
        return self._data.get("DhwFlowRate", None)

    @property
    def hw_temperature(self) -> str:
        """Get Dhw1Temperature"""
        return tf._from_wiser_temp(self._data.get("Dhw1Temperature", None), "current")

    @property
    def relative_modulation_level(self) -> int:
        """Get RelativeModulationLevel"""
        if self._data.get("RelativeModulationLevel"):
            return int(self._data.get("RelativeModulationLevel", 0) / 10)
        return None

    @property
    def slave_status(self) -> int:
        """Get SlaveStatus"""
        return self._data.get("SlaveStatus", None)

    @property
    def json_data(self) -> dict:
        return self._data


class _WiserOpenThermExtendedDiagnostics:
    """Data structure for Opentherm extended diagnostics."""

    def __init__(self, data: dict[str, int | str]):
        self._data = data

    @property
    def unsuccessful_burner_starts(self) -> int:
        """Get unsuccessfulBurnerStarts"""
        return self._data.get("unsuccessfulBurnerStarts", 0)

    @property
    def number_flame_signal_too_low(self) -> int:
        """Get numberFlameSignalTooLow"""
        return self._data.get("numberFlameSignalTooLow", 0)

    @property
    def oem_specific_service_code(self) -> int:
        """Get oemSpecificServiceCode"""
        return self._data.get("oemSpecificServiceCode", 0)

    @property
    def successful_burner_starts(self) -> int:
        """Get successfulBurnerStarts"""
        return self._data.get("successfulBurnerStarts", 0)

    @property
    def ch_pump_starts(self) -> int:
        """Get chPumpStarts"""
        return self._data.get("chPumpStarts", 0)

    @property
    def dhw_pump_or_valve_starts(self) -> int:
        """Get dhwPumpOrValveStarts"""
        return self._data.get("dhwPumpOrValveStarts", 0)

    @property
    def burner_starts_during_dhw_mode(self) -> int:
        """Get burnerStartsDuringDhwMode"""
        return self._data.get("burnerStartsDuringDhwMode", 0)

    @property
    def burner_hours(self) -> int:
        """Get burnerHours"""
        return self._data.get("burnerHours", 0)

    @property
    def ch_pump_hours(self) -> int:
        """Get chPumpHours"""
        return self._data.get("chPumpHours", 0)


class _WiserOpentherm(object):
    """Data structure for Opentherm data"""

    def __init__(
        self,
        wiser_rest_controller: _WiserRestController,
        data: dict,
        enabled_status: str,
    ):
        self._data = data
        self._enabled_status = enabled_status
        self._wiser_rest_controller = wiser_rest_controller

    @property
    def id(self) -> int:
        """Return system id."""
        return 0

    @property
    def ch_flow_active_lower_setpoint(self) -> float:
        """Get chFlowActiveLowerSetpoint"""
        return tf._from_wiser_temp(
            self._data.get("chFlowActiveLowerSetpoint", None), "current"
        )

    @property
    def ch_flow_active_upper_setpoint(self) -> float:
        """Get chFlowActiveUpperSetpoint"""
        return tf._from_wiser_temp(
            self._data.get("chFlowActiveUpperSetpoint", None), "current"
        )

    @property
    def ch1_flow_enabled(self) -> bool:
        """Get ch1FlowEnable"""
        return self._data.get("ch1FlowEnable", False)

    @property
    def ch1_flow_setpoint(self) -> float:
        """Get ch1FlowSetpoint"""
        return tf._from_wiser_temp(self._data.get("ch1FlowSetpoint", None), "current")

    @property
    def ch2_flow_enabled(self) -> bool:
        """Get ch2FlowEnable"""
        return self._data.get("ch2FlowEnable", False)

    @property
    def ch2_flow_setpoint(self) -> float:
        """Get ch2FlowSetpoint"""
        return tf._from_wiser_temp(self._data.get("ch2FlowSetpoint", None), "current")

    @property
    def connection_status(self) -> str:
        """Get opentherm connection status"""
        return self._enabled_status

    @property
    def enabled(self) -> bool:
        """Get Enabled"""
        return self._data.get("Enabled", False)

    @property
    def hw_enabled(self) -> bool:
        """Get dhwEnable"""
        return self._data.get("dhwEnable", False)

    @property
    def hw_flow_setpoint(self) -> float:
        """Get dhwFlowSetpoint"""
        return tf._from_wiser_temp(self._data.get("dhwFlowSetpoint", None), "current")

    @property
    def operating_mode(self) -> str:
        """Get operatingMode"""
        return self._data.get("operatingMode", None)

    @property
    def operational_data(self) -> _WiserOpenThermOperationalData:
        return _WiserOpenThermOperationalData(self._data.get("operationalData", {}))

    @property
    def boiler_parameters(self) -> _WiserOpenThermBoilerParameters:
        return _WiserOpenThermBoilerParameters(
            self._data.get("preDefinedRemoteBoilerParameters", {})
        )

    @property
    def extended_diagnostics(self) -> _WiserOpenThermExtendedDiagnostics:
        return _WiserOpenThermExtendedDiagnostics(
            self._data.get("extendedDiagnostics", {})
        )

    @property
    def room_setpoint(self) -> float:
        """Get roomTemperature"""
        return tf._from_wiser_temp(self._data.get("roomSetpoint", None), "current")

    @property
    def room_temperature(self) -> float:
        """Get roomTemperature"""
        return tf._from_wiser_temp(self._data.get("roomTemperature", None), "current")

    @property
    def tracked_room_id(self) -> int:
        """Get TrackedRoomId"""
        return self._data.get("TrackedRoomId", None)

    @property
    def json_data(self) -> dict:
        return self._data

    async def set_opentherm_parameter(self, endpoint: str, cmd_data: str) -> bool:
        """Allow settign of opentherm param"""
        return await self._wiser_rest_controller._do_hub_action(
            WiserRestActionEnum.PATCH,
            f"{WISERHUBOPENTHERM}{endpoint}",
            cmd_data,
        )
