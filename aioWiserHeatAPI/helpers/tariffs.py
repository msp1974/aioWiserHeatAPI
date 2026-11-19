"""
Handles tariffs data
"""
# new feature for tariffs energy monitoring
        # 
        # 
        

import inspect
from ..import _LOGGER

import time
from datetime import datetime, timedelta

from ..const import (
    TEXT_UNABLE,
    TEXT_UNKNOWN,
    WISERTARIFFS,
    WiserTariffTypeEnum,
    WiserEnergyTariffTypeEnum,
    )

#from .rest_controller import _WiserRestController


class _Tariffinterval(object):
    """Data structure for Tariff interval"""

    def __init__(self, data: dict):
        self._data = data

    @property
    def id(self) -> int:
        """Get delivered power"""
        return self._data.get("id", None)

    @property
    def start(self) -> datetime:
        """Get the beginning of the interval"""
        return self._data.get("from", None)

    @property
    def end(self) -> datetime:
        """Get the end of the interval"""
        return self._data.get("to", None)

    @property
    def price(self) -> float:
        """Get the price during this interval"""
        return self._data.get("price", None)

class _TariffForecast(object):
    """Data structure for Tariff interval"""

    def __init__(self, data: dict):
        self._data = data
        self._tariffintervals = []

        _LOGGER.info(
                "LGO Wiser hub helpers WiserTariffs Forecast 59 - %s ",  (self._data)
        )
        _LOGGER.info(
                "LGO Wiser hub helpers WiserTariffs Forecast tariffintervals[] 61 - %s ",  self._tariffintervals
        )
        for interval in self._data:
            self._tariffintervals.append(_Tariffinterval(interval)) 
            _LOGGER.info(
                "LGO Wiser hub helpers WiserTariffs Forecast tariffintervals[] 69 - %s ",  vars(_Tariffinterval(interval))
            )

    @property
    def test(self) -> bool:
        """Get id of automation"""
        return True

    @property
    def tariff_interval(self) -> _Tariffinterval:
        """Get id of automation"""
        return _Tariffinterval(self._data) 

class _TariffCurrentDay(object):
    """Data structure for Tariff interval"""

    def __init__(self, data: dict):
        self._data = data

class _EnergyTariffComplete(object  ):
    """Data structure for Energy Tariff"""

    def __init__(self, data: dict):
        self._tariff_data = data

    @property
    def forecast(self) -> _TariffForecast:
        """Get tariff forecast data"""
        _LOGGER.info(
                "LGO Wiser hub helpers WiserTariffs Forecast 74 - %s ",  vars(_TariffForecast(self._tariff_data.get("Forecast")))
        )
#        return _TariffForecast(self._tariff_data.get("Forecast", {}))
        return _TariffForecast(self._tariff_data.get("Forecast"))
                                                             
    @property
    def current_day(self) -> _TariffCurrentDay:
        """Get id of automation"""
        return _TariffCurrentDay(self._tariff_data.get("CurrentDay", {}))

    @property
    def daily_average(self) -> float:
        """Get daily average tariff"""  
        return self._tariff_data.get("DailyAverage", 0.0)

    @property
    def daily_averagex100(self) -> float:
        """Get daily average tariff"""  
        return self._tariff_data.get("DailyAverage100Multiplier", 0.0)

    @property
    def current_price(self) -> float:
        """Get daily average tariff"""  
        
        return round(self._tariff_data.get("CurrentPrice", 0.0),4)    
    @property
    def current_pricex100(self) -> float:
        """Get daily average tariff"""  
        return self._tariff_data.get("CurrentPrice100Multiplier", 0.0)


class _EnergyTariffInfo(object):#Marlene1

    """Data structure for Energy Tariff"""

    def __init__(self, data: dict):
        self._tariff_data = data
        _LOGGER.info(
                f"LGO Wiser hub helpers EnergyTariff 106 -  {self._tariff_data}  "
                )
    @property
    def daily_average(self) -> float:
        """Get daily average tariff"""  
        return self._tariff_data.get("DailyAverage", 0.0)
    
    @property
    def daily_averagex100(self) -> float:
        """Get daily average tariff"""  
        return self._tariff_data.get("DailyAverage100Multiplier", 0.0)

    @property
    def current_price(self) -> float:
        """Get daily average tariff"""  
        _LOGGER.info(
                "LGO Wiser hub helpers WiserTariffs EnergyTarifInfo 121 current_price - %s", self._tariff_data.get("CurrentPrice")
                )
        return self._tariff_data.get("CurrentPrice", 0.0)
    
    @property
    def current_pricex100(self) -> float:
        """Get daily average tariff"""  
        return self._tariff_data.get("CurrentPrice100Multiplier", 0.0)

class _WiserTariffs_end:
    def __init__(
        self,  tariff_data: dict
    ):
        #self._wiser_rest_controller = wiser_rest_controller
        self._tariff_data = tariff_data
        _LOGGER.info(
                "LGO Wiser hub WiserTariffs init 134 - %s",  self._tariff_data ) # {self._tariff_data.current_price} {self._tariff_data.daily_average} {self._tariff_data.energy_tariff}
                
         
    async def _send_command(self, cmd: dict) -> bool:
        """
        Send system control command to Wiser Hub
        param cmd: json command structure
        return: boolen - true = success, false = failed
        """
        result = await self._wiser_rest_controller._send_command(WISERTARIFFS, cmd)
        if result:
            _LOGGER.debug(
                "Wiser hub - %s command successful", format(inspect.stack()[1].function)
            )
            return True
        return False
    """
    
    @property
    def energy_tariff(self) -> _EnergyTariff:
        _LOGGER.info(
                "LGO Wiser hub WiserTariffs Energytariff 155 - %s ",  self._tariff_data 
                # {self._tariff_data.current_price} {self._tariff_data.daily_average} {self._tariff_data.energy_tariff}
                )
        return (
            _EnergyTariff(self._tariff_data.get("EnergyTariff"))
            )
    """

    @property
    def current_price1(self) -> float:
        """Get current scheduled setting (temp or state)"""
        if self._type == WiserTariffTypeEnum.energytariff.value:
            _LOGGER.info(
                f"LGO Wiser hub helpers WiserTariffs 168 current_price -  {self._tariff_data.get("CurrentPrice", 0.0)} " # {self._tariff_data.current_price} {self._tariff_data.daily_average} {self._tariff_data.energy_tariff}
                )
            return (
                self._tariff_data.get("EnergyTariff").get("CurrentPrice", 0.0)
                )
        

    @property
    def current_price(self) -> float:
        """Get daily average tariff"""  
        _LOGGER.info(
                f"LGO Wiser hub WiserTariffs 179 current_price -  {self._tariff_data.EnergyTariff.get("CurrentPrice", 0.0)} " # {self._tariff_data.current_price} {self._tariff_data.daily_average} {self._tariff_data.energy_tariff}
                )
        return self._tariff_data.get("EnergyTariff").get("CurrentPrice", 0.0)

    @property
    def daily_average(self) -> float:
        """Get daily average tariff"""  
        _LOGGER.info(
                f"LGO Wiser hub WiserTariffs 187 daily -  {self._tariff_data.get("EnergyTariff").get("DailyAverage", 0.0)} " # {self._tariff_data.current_price} {self._tariff_data.daily_average} {self._tariff_data.energy_tariff}
                )
        return self._tariff_data.get("EnergyTariff").get("DailyAverage", 0.0)
    @property
    def daily_averagex100(self) -> float:
        """Get daily average tariff"""  
        return self._tariff_data.get("EnergyTariff").get("DailyAverage100Multiplier", 0.0)

    
    @property
    def current_pricex100(self) -> float:
        """Get daily average tariff"""  
        return self._tariff_data.get("EnergyTariff").get("CurrentPrice100Multiplier", 0.0)

class _WiserTariffs:
    def __init__(
        self,tariff_data: dict
    ):
        self._tariff_data = tariff_data
        _LOGGER.info(
                "LGO Wiser hub helpers WiserTariffs init 208 - %s",  self._tariff_data ) 
                
         

    @property
    def current_price(self) -> float:
        """Get daily average tariff"""  

    #Debug LGO    
        _LOGGER.info(
                "LGO Wiser hub helpers WiserTariffs current_price 216 "  
                )
        _LOGGER.info(
                "LGO Wiser hub helpers WiserTariffs 216 current_price - %s", self._tariff_data.get("EnergyTariff").get("CurrentPrice")
                )
    # end Debug LGO

        return self._tariff_data.get("EnergyTariff").get("CurrentPrice", 0.0)
    
    @property
    def energy_tariff(self) -> _EnergyTariffInfo:
    #Debug LGO
        _LOGGER.info(
                "LGO Wiser hub helpers WiserTariffs energy_tarif 225 "  
                )
                
        _LOGGER.info(
                "LGO Wiser hub helpers WiserTariffs EnergytariffInfo 223 - %s ",  vars(_EnergyTariffInfo(self._tariff_data.get("EnergyTariff")))
        )
    #Debug LGO            )
        return (
            #_EnergyTariffInfo(self._tariff_data.get("EnergyTariff"))
            _EnergyTariffComplete(self._tariff_data.get("EnergyTariff"))
            )


