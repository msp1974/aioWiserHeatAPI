from ..const import (
    TEMP_ERROR,
    TEMP_MINIMUM,
    TEMP_MAXIMUM,
    TEMP_OFF,
    TEMP_HW_OFF,
    TEMP_HW_ON,
    MAX_BOOST_INCREASE,
    WiserUnitsEnum,
    WiserTempLimitsEnum,
)


class _WiserTemperatureFunctions(object):
    # -----------------------------------------------------------
    # Support Functions
    # -----------------------------------------------------------
    @staticmethod
    def _to_wiser_temp(
        temp: float,
        type: str = "heating",
        units: WiserUnitsEnum = WiserUnitsEnum.metric,
    ) -> int:
        """
        Converts from degrees C to wiser hub format
        param temp: The temperature to convert
        param type: Can be heating (default), hotwater or delta
        return: Integer
        """
        temp = int(_WiserTemperatureFunctions._validate_temperature(temp, type) * 10)

        # Convert to metric if imperial units set
        if units == WiserUnitsEnum.imperial:
            temp = _WiserTemperatureFunctions._convert_from_F(temp)

        return temp

    @staticmethod
    def _from_wiser_temp(
        temp: int,
        type: str = "heating",
        units: WiserUnitsEnum = WiserUnitsEnum.metric,
    ) -> float:
        """
        Converts from wiser hub format to degrees C
        param temp: The wiser temperature to convert
        return: Float
        """
        if temp is not None:
            if abs(temp) >= TEMP_ERROR:
                # Fix high value from hub when lost sight of iTRV
                return None
            else:
                temp = _WiserTemperatureFunctions._validate_temperature(
                    round(temp / 10, 1), type
                )

            # Convert to imperial if imperial units set
            if units == WiserUnitsEnum.imperial:
                temp = _WiserTemperatureFunctions._convert_to_F(temp)

            return temp
        return None

    @staticmethod
    def _is_valid_temp(temp: float, hw: bool = False) -> bool:
        if hw and temp in [TEMP_HW_ON, TEMP_HW_OFF]:
            return True
        elif temp == TEMP_OFF or (temp >= TEMP_MINIMUM and temp <= TEMP_MAXIMUM):
            return True
        return False

    @staticmethod
    def _validate_temperature(temp: float, type: str = "heating") -> float:
        """
        Validates temperature value is in range of Wiser Hub allowed values
        Sets to min or max temp if value exceeds limits
        param temp: temperature value to validate
        return: float
        """

        # Get limits type
        limits = WiserTempLimitsEnum[type].value
        if limits.get("type") == "onoff":
            if temp in [limits.get("on"), limits.get("off")]:
                return temp
            return limits.get("off")

        if limits.get("type") == "range":
            if temp >= TEMP_ERROR:
                return limits.get("min")
            elif temp > limits.get("max"):
                return limits.get("max")
            elif temp < limits.get("min") and temp != limits.get("off", TEMP_OFF):
                return limits.get("min")
            else:
                return temp

        raise ValueError("Invalid temperature type for validation")

    @staticmethod
    def _convert_from_F(temp: float) -> float:
        """
        Convert F temp to C
        param temp: temp in F to convert
        return: float
        """
        return round((temp - 32) * 5 / 9, 1)

    @staticmethod
    def _convert_to_F(temp: float) -> float:
        """
        Convert C temp to F
        param temp: temp in C to convert
        return: float
        """
        return round((temp * 9 / 5) + 32, 1)
