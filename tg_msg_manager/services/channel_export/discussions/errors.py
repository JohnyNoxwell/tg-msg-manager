class ChannelDiscussionError(Exception):
    """Base error for channel discussion export components."""


class ChannelDiscussionResolveError(ChannelDiscussionError):
    """Raised when linked discussion resolution fails unexpectedly."""


class ChannelDiscussionFetchError(ChannelDiscussionError):
    """Raised by iterator-style fetch APIs when one thread cannot be fetched."""


class ChannelDiscussionStateError(ChannelDiscussionError):
    """Raised when discussion export state cannot be loaded safely."""
