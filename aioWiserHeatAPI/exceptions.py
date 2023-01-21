# Exception Handlers
class WiserHubConnectionError(Exception):
    pass


class WiserHubAuthenticationError(Exception):
    pass


class WiserHubRESTError(Exception):
    pass


class WiserScheduleError(Exception):
    pass


class WiserScheduleInvalidTime(Exception):
    pass


class WiserScheduleInvalidSetting(Exception):
    pass


class WiserExtraConfigError(Exception):
    pass


class WiserHubNotImplementedError(Exception):
    # _LOGGER.info("Function not yet implemented")
    pass
