class ChannelExportError(Exception):
    pass


class ChannelResolveError(ChannelExportError):
    pass


class InvalidChannelError(ChannelExportError):
    pass


class ChannelExportStateError(ChannelExportError):
    pass
