"""
Handles equipment devices
"""
# new implementation for equipments
        #add notification for over or under power
        # clean up the file helpers/equipment.py

import inspect
from . import _LOGGER

from .const import TEXT_UNABLE, TEXT_UNKNOWN,  WISEREQUIPMENT
#from .helpers.device import _WiserDevice
from .helpers.equipment import _WiserEquipment

from .rest_controller import _WiserRestController

class _WiserEquipmentPower(object):
    """Data structure for Equipment Power Info"""

    def __init__(self, data: dict):
        self._data = data

    @property
    def current_summation_delivered(self) -> int:
        """Get delivered power"""
        return self._data.get("CurrentSummationDelivered", None)

    @property
    def current_summation_received(self) -> int:
        """Get received power"""
        return self._data.get("CurrentSummationReceived", None)

    @property
    def total_active_power(self) -> int:
        """Get total active power"""
        return self._data.get("TotalActivePower", None)

    @property
    def active_power(self) -> int:
        """Get active power"""
        return self._data.get("ActivePower", None)

    @property
    def rms_current(self) -> int:
        """Get rms current"""
        return self._data.get("RMSCurrent", None)

    @property
    def rms_voltage(self) -> int:
        """Get rms voltage"""
        return self._data.get("RMSVoltage", None)


class _WiserEquipmentPowerNotificationInfo(_WiserEquipment):
    """Data structure for Equipment Power Info Notification"""
   
    def __init__(self, data: dict):
        self._data = data
        self._wiser_rest_controller = _WiserRestController
        
    @property
    def period_mins(self) -> int:
        """Get period in minutes"""
        return self._data.get("PeriodMins", 0)

    @property
    def limit(self) -> int:
        """Get limit"""
        return self._data.get("Limit", 0)

    @property
    def enabled(self) -> bool:
        """Get if notification enabled"""
        return self._data.get("Enabled", False)

    """Get the under and over power notification info
    """
    async def set_enabled(self, enabled: bool):
        if await self._wiser_rest_controller._send_command(
            WISEREQUIPMENT.format(self._equipment_id),
                {
                    "UnderPowerNotification": {
                        "PeriodMins": self._data.get("PeriodMins", 0),
                        "Limit": self._data.get("Limit", 0),
                        "Enabled": str(enabled).lower()
                    }
                }
            ):
            self._enabled = enabled
            return True
    


class _WiserEquipments:
    """Class representing a Wiser Equipment device"""

    def __init__(
        self, wiser_rest_controller: _WiserRestController, equipment_data: dict
    ):
        self._wiser_rest_controller = wiser_rest_controller
        self._equipment_data = equipment_data
        
        
    async def _send_command(self, cmd: dict) -> bool:
        """
        Send system control command to Wiser Hub
        param cmd: json command structure
        return: boolen - true = success, false = failed
        """
        
        result = await self._wiser_rest_controller._send_command(WISEREQUIPMENT, cmd)
        if result:
            _LOGGER.debug(
                "Wiser Equipment - %s command successful", format(inspect.stack()[1].function)
            )
            return True
        return False

    @property
    def equipment(self) -> _WiserEquipment | None:
        """Get equipment data"""

        return (
            _WiserEquipment(self._equipment_data)
            if self._equipment_data.get("id")
            else None
        )

    @property
    def id(self) -> int:
        return self._equipment_data.get("id", 0)

    @property
    def equipment_id(self) -> int:
        """Get id of equipment"""
        return self._equipment_data.get("id", 0)

    @property
    def device_application_instance_type(self) -> str:
        """Get id of equipment"""
        return self._equipment_data.get("DeviceApplicationInstanceType", TEXT_UNKNOWN)

    @property
    def device_application_instance_id(self) -> int:
        """Get id of equipment"""
        return self._equipment_data.get("DeviceApplicationInstanceId", 0)

    @property
    def name(self) -> str:
        return self._equipment_data.get("EquipmentName", TEXT_UNKNOWN)

    @property
    def power(self) -> _WiserEquipmentPower:
        """Get the power info"""
        return _WiserEquipmentPower(self._equipment_data)

    @property
    def grid_limit(self) -> int:
        """Get grid limit"""
        return self._equipment_data.get("GridLimit", 0)

    @property
    def grid_limit_uom(self) -> str:
        """Get grid limit uom"""
        return self._equipment_data.get("GridLimitUom", TEXT_UNKNOWN)

    @property
    def self_consumption(self) -> bool:
        """Get self consumption"""
        return self._equipment_data.get("SelfConsumption", False)

    @property
    def energy_export(self) -> str:
        """Get energy export status"""
        return self._equipment_data.get("EnergyExport", TEXT_UNABLE)

    """Get the under and over power notification info"""
    @property
    def over_power_notification(self) -> _WiserEquipmentPowerNotificationInfo | None:
        """Get notification info"""
        return (_WiserEquipmentPowerNotificationInfo(self._equipment_data.get("OverPowerNotification") )     
            if self._equipment_data.get("OverPowerNotification")
            else None
        )
        """ """

    @property
    def under_power_notification(self) -> _WiserEquipmentPowerNotificationInfo | None:
        """Get notification info"""
        return (_WiserEquipmentPowerNotificationInfo(self._equipment_data.get("UnderPowerNotification") ) 
            if self._equipment_data.get("UnderPowerNotification")
            else None
        )    
        """ """
            
    """Get the under and over power notification info"""

    """send command to the under and over power notification info"""
    @property 
    def under_power_notification_period_mins(self) -> int:
        """Get under power notification period in minutes"""
        
        return (self._equipment_data.get("UnderPowerNotification").get("PeriodMins", 0)
            if self.under_power_notification
            else None)

    @property 
    def under_power_notification_limit(self) -> int:
        """Get under power notification limit"""
        
        return (self._equipment_data.get("UnderPowerNotification").get("Limit", 0)
            if self.under_power_notification
            else None)

    @property 
    def under_power_notification_enabled(self) -> bool:
        """Get under power notification limit"""
        
        return (self._equipment_data.get("UnderPowerNotification").get("Enabled", False)
            if self.under_power_notification
            else None)

    async def set_under_power_notification_enabled(self, enabled: bool):

        if await self._wiser_rest_controller._send_command(
            WISEREQUIPMENT.format(self._equipment_data.get("id", 0)),
                {
                    "UnderPowerNotification": {
                        "PeriodMins": self._equipment_data.get("UnderPowerNotification").get("PeriodMins", 0),
                        "Limit": self._equipment_data.get("UnderPowerNotification").get("Limit", 0),
                        "Enabled": str(enabled).lower()
                    }
                }
            ):

            self._under_power_notification_enabled = enabled

            return True

    @property 
    def over_power_notification_period_mins(self) -> int:
        """Get under power notification period in minutes"""
        
        return (self._equipment_data.get("OverPowerNotification").get("PeriodMins", 0)
            if self.over_power_notification
            else None)


    @property 
    def over_power_notification_limit(self) -> int:
        """Get over power notification limit"""
        
        return (self._equipment_data.get("OverPowerNotification").get("Limit", 0)
            if self.over_power_notification
            else None)

    @property 
    def over_power_notification_enabled(self) -> bool:
        """Get over power notification limit"""
        
        return (self._equipment_data.get("OverPowerNotification").get("Enabled", False)
            if self.over_power_notification
            else None)

    async def set_over_power_notification_enabled(self, enabled: bool):
        if await self._wiser_rest_controller._send_command(
            WISEREQUIPMENT.format(self._equipment_data.get("id", 0)),
                {
                    "OverPowerNotification": {
                        "PeriodMins": self._equipment_data.get("OverPowerNotification").get("PeriodMins", 0),
                        "Limit": self._equipment_data.get("OverPowerNotification").get("Limit", 0),
                        "Enabled": str(enabled).lower()
                    }
                }
            ):
            
            self._over_power_notification_enabled = enabled

            return True


class _WiserEquipmentsCollection(object):
    """Class representing collection of Equipment devices"""

    
    def __init__(
        self, wiser_rest_controller: _WiserRestController, equipments_data: dict
    ):
        self._equipments_data = equipments_data
        self._equipments = []
        self._wiser_rest_controller = wiser_rest_controller
        self._build()

    def _build(self):
        for equipment in self._equipments_data:

            self._equipments.append(
                _WiserEquipments(self._wiser_rest_controller, equipment)
            )

    @property
    def all(self) -> list[_WiserEquipments]:
        return list(self._equipments)

    @property
    def count(self) -> int:
        """Return number of equipments"""
        return len(self.all)

    def get_equip_by_id(self, equipment_id: int) -> _WiserEquipment:
        """
        Gets a Equipment object from the device id
        param id: id of equipments
        return: _WiserEquipment object
        """
        try:
            return [
                equipment
                for equipment in self.all
                if equipment.id == equipment_id
            ][0]
        except IndexError:
            return None

    def get_by_equipment_id(self, equipment_id: int) -> _WiserEquipment:
        """
        Gets a Equipment object from the equipment id
        param id: id of equipment
        return: _WiserEquipment object
        """
        try:
            return [
                equipment
                for equipment in self.all
                if equipment.id == equipment_id
            ][0]
        except IndexError:
            return None

