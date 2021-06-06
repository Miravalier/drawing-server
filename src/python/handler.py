# Global table of message types to handlers
player_contexts = {}
request_handlers = {}


class InvalidParameter(Exception):
    pass


# Register decorator
def register(message_type, arguments=None):
    if arguments is None:
        arguments = []

    def validator(message):
        for name, cls in arguments:
            value = message.get(name, InvalidParameter)
            if value is InvalidParameter:
                raise InvalidParameter(
                    "{} request missing required parameter: '{}'".format(
                        message_type,
                        name
                    )
                )
            elif not isinstance(value, cls):
                raise InvalidParameter(
                    "{} parameter '{}' must be of type '{}', not '{}'".format(
                        message_type,
                        name,
                        cls.__name__,
                        type(value).__name__
                    )
                )

    def handler(func):
        request_handlers[message_type] = (validator, func)
        return func

    return handler
