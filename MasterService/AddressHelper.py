
# Manages secondaries address
class AddressHelper():
    def __init__(self) -> None:
        self.channels = [1, 2, 5, 4, 3]
        pass

    def GetChannels(self):
        return self.channels