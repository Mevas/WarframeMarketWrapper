class WarframeMarketException(Exception):
    """The base exception class.

    .. versionadded:: 1.0.0

        Necessary to handle pre-response exceptions

    """

    pass


class WarframeMarketError(WarframeMarketException):
    """The base exception class for all response-related exceptions.

    .. attribute:: response

        The response object that triggered the exception

    .. attribute:: code

        The response's status code

    .. attribute:: errors

        The list of errors (if present) returned by Warframe Market's API
    """

    def __init__(self, resp):
        """Initialize our exception class."""
        super(WarframeMarketError, self).__init__(resp)
        #: Response code that triggered the error
        self.response = resp
        self.code = resp.status_code
        self.errors = []
        try:
            error = resp.json()
            #: Message associated with the error
            self.msg = error.get("message")
            #: List of errors provided by Warframe Market
            if error.get("errors"):
                self.errors = error.get("errors")
        except Exception:  # Amazon S3 error
            self.msg = resp.content or "[No message]"

    def __repr__(self):
        return "<{0} [{1}]>".format(
            self.__class__.__name__, self.msg or self.code
        )

    def __str__(self):
        return "{0} {1}".format(self.code, self.msg)

    @property
    def message(self):
        """The actual message returned by the API."""
        return self.msg


class ResponseError(WarframeMarketError):
    """The base exception for errors stemming from Warframe Market responses."""

    pass


class BadRequest(ResponseError):
    """Exception class for 400 responses."""

    pass


class AuthenticationFailed(ResponseError):
    """Exception class for 401 responses.

    Possible reasons:

    - Need one time password (for two-factor authentication)
    - You are not authorized to access the resource
    """

    pass


class ForbiddenError(ResponseError):
    """Exception class for 403 responses.

    Possible reasons:

    - Too many requests (you've exceeded the ratelimit)
    - Too many login failures
    """

    pass


class NotFoundError(ResponseError):
    """Exception class for 404 responses."""

    pass


class MethodNotAllowed(ResponseError):
    """Exception class for 405 responses."""

    pass


class NotAcceptable(ResponseError):
    """Exception class for 406 responses."""

    pass


class Conflict(ResponseError):
    """Exception class for 409 responses.

    Possible reasons:

    - Head branch was modified (SHA sums do not match)
    """

    pass


class UnprocessableEntity(ResponseError):
    """Exception class for 422 responses."""

    pass


class ClientError(ResponseError):
    """Catch-all for 400 responses that aren't specific errors."""

    pass


class ServerError(ResponseError):
    """Exception class for 5xx responses."""

    pass


class UnavailableForLegalReasons(ResponseError):
    """Exception class for 451 responses."""

    pass


error_classes = {
    400: BadRequest,
    401: AuthenticationFailed,
    403: ForbiddenError,
    404: NotFoundError,
    405: MethodNotAllowed,
    406: NotAcceptable,
    409: Conflict,
    422: UnprocessableEntity,
    451: UnavailableForLegalReasons,
}


def generate_error(response):
    """Return the appropriate initialized exception class for a response."""
    klass = error_classes.get(response.status_code)
    if klass is None:
        if 400 <= response.status_code < 500:
            klass = ClientError
        if 500 <= response.status_code < 600:
            klass = ServerError
    return klass(response)
