"""
scriptlib.utils.strutils

Miscellaneous utility functions for manipulating
strings.
"""

def expand_placeholders(
        message: str,
        placeholders: dict
    ) -> str:
    """
    Expands placeholders into a message with format:
        %placeholder%
    
    Arguments:
        message: str - Message to format
        placeholders: dict[str, str] - Placeholders to expand
            ({placeholder_name: replace_with})
    """

    for placeholder, value in placeholders.items():
        message = message.replace(
            f"%{placeholder}%",
            str(value)
        )

    return message

def pad_to(
        value: str,
        length: int,
        trunc: bool = True
    ) -> str:
    """
    Pads a string with to the specified number of spaces.
    
    Arguments:
        value: str - Message to pad
        length: int - Length to pad to
        trunc: bool = True - Truncate string if greater than length
    """

    if trunc:
        value = value[:length]

    return value + (" " * (length - len(value)))