from enum import Enum, unique

SERVICE_NAME = "master-service"

@unique
class ConfigKeys(Enum):
    PORT = "PORT"
    ADDRESS_HELPER_PORT = "ADDRESS_HELPER_PORT"

    RETRIES_TO_SECONDARY = "RETRIES_TO_SECONDARY"
