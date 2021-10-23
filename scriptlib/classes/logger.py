"""
scriptlib.classes.logger

Handles all fancy logging to the terminal.
"""

import time
from typing import Optional, Union

from ..utils import (
    colors,
    exceptions,
    strutils,
    timeutils
)

import scriptlib

class Logger:
    """
    Base class for the scriptlib logger.
    """
    def __init__(
            self
        ) -> None:

        self.log_types = {
            "warn": "yellow",
            "error": "red",
            "success": "green",
            "start": "cyan",
            "stop": "cyan",
            "close": "cyan",
            "info": "default",
            "obj": "magenta",
            "ask": "magenta",
            "debug": "magenta"
        }

        self.colors = colors.termcolors

        self.ready = False

        self.timer = time.time()

        self.logging = {
            "tasks": False,
            "start": True,
            "init": True,
            "stop": True,
            "shutdown": True,
            "unhandlederror": True,
            "config": True,
            "ws": True,
            "subprocess": True,
            "user": True,
            "ask": True,
            "debug": True,
            "menu": True
        }

        self.format = {
            "log": "%color%%reverseopt%%bold%%timep% %typep% %reset%%color%%reverseopt%%boldopt%%message%%reset%",
            "step": "                            %color%%reverseopt%%bold%→ %reset%%color%%reverseopt%%boldopt%%message%%reset%",
            "long": "                            %color%%reverseopt%%bold%→ %reset%%color%%reverseopt%%boldopt%%message%%reset%",
            "raw": "%color%%reverseopt%%boldopt%%message%%reset%",
            "ask": "%color%%reverseopt%%bold%%timep% %typep% %reset%%color%%reverseopt%%boldopt%%message% %reset%%color%[%hint%]%reset%",
        }

        self.format_type = {}

    def prep(
            self
        ) -> None:
        """
        Loads up customized values from the config.
        """

        global script
        from scriptlib import script

        for name, value in script.config.log_colors.items():
            if name not in self.log_types:
                raise exceptions.InitError(f"Log type {name} doesn't exist")

            if not value.startswith("&"):
                if value not in self.colors:
                    raise exceptions.InitError(f"Terminal color {value} doesn't exist")

            self.log_types[name] = value

        for name, value in script.config.log_formats.items():
            if name not in self.format:
                raise exceptions.InitError(f"Log format type {name} doesn't exist")

            self.format[name] = value

        for name, value in script.config.logging.items():
            if name not in self.logging:
                raise exceptions.InitError(f"Log category {name} doesn't exist")

            self.logging[name] = value

        self.ready = True

    def get_placeholders(
            self,
            log_type,
            category,
            message,
            bold,
            color,
            reversed
        ) -> dict:
        """
        Returns a dict of all used placeholders for a message.

        Arguments:
            log_type: str - Log type of message
            category: str - Category of message
            message: str
            bold: bool
            color: str
            reversed: bool

        Returns:
            placeholders: dict[str, str] - All placeholders
        """

        current_time = time.time() - self.timer
        time_str = str(round(current_time, 3))
        time_f = timeutils.get_duration(time_str.split(".", 1)[0])
        
        return {
            "color": color,
            "bold": self.colors["bold"],
            "reset": self.colors["reset"],
            "underline": self.colors["underline"],
            "reversed": self.colors["reversed"],
            "reverseopt": self.colors["reversed"] if reversed else "",
            "boldopt": self.colors["bold"] if bold else "",
            "time": time_str,
            "timep": strutils.pad_to(f"[{time_str}]", 14),
            "timef": time_f,
            "timepf": strutils.pad_to(time_f, 16),
            "typep": strutils.pad_to(f"[{log_type.upper()}]", 10),
            "logtype": log_type.upper(),
            "logtypel": log_type,
            "message": message,
            "category": category
        }

    def log(
            self,
            *args,
            **kwargs
        ) -> None:
        """
        Logs something.
        
        Arguments:
            log_type: str
            category: str
            message: str
            bold: bool = False
            reversed: bool = False
            color: str = None
            placeholder_ext: dict = {}
        """

        self.log_type(
            "log",
            *args,
            **kwargs
        )

    def log_step(
            self,
            *args,
            **kwargs
        ) -> None:
        """
        Logs a single step in an operation.
        
        Arguments:
            log_type: str
            category: str
            message: str
            bold: bool = False
            reversed: bool = False
            color: str = None
            placeholder_ext: dict = {}
        """

        self.log_type(
            "step",
            *args,
            **kwargs
        )

    def log_long(
            self,
            log_type: str,
            category: str,
            messages: Union[list, str],
            bold: bool = False,
            reversed: bool = False,
            color: Optional[str] = None,
            remove_blank_lines: bool = False,
            extra_line: bool = False
        ) -> None:
        """
        Logs a multi-line string.
        
        Arguments:
            log_type: str
            category: str
            message: list|str
            bold: bool = False
            reversed: bool = False
            color: str = None
            placeholder_ext: dict = {}
        """

        if type(messages) == str:
            messages = messages.split("\n")

        for line in messages:
            if line.strip() == "":
                continue

            self.log_type(
                "long",
                log_type,
                category,
                line,
                bold,
                reversed,
                color
            )

        if extra_line:
            scriptlib.terminal.log(" ", True)

    def log_raw(
            self,
            *args,
            **kwargs
        ) -> None:
        """
        Logs something with no decorations.
        
        Arguments:
            log_type: str
            category: str
            message: str
            bold: bool = False
            reversed: bool = False
            color: str = None
            placeholder_ext: dict = {}
        """
        

        self.log_type(
            "raw",
            *args,
            **kwargs
        )
    
    def log_ask(
            self,
            message: str,
            hint: str
        ) -> None:
        """
        Logs a question asked to the user.

        Use scriptlib.terminal.ask instead.
        
        Arguments:
            message: str
            hint: str
        """

        self.log_type(
            "ask",
            "ask",
            "ask",
            message,
            bold = True,
            placeholder_ext = {
                "hint": hint
            }
        )

    def log_type(
            self,
            name: str,
            log_type: str,
            category: str,
            message: str,
            bold: bool = False,
            reversed: bool = False,
            color: Optional[str] = None,
            placeholder_ext: dict = {}
        ) -> None:
        """
        Internal function to log a message of specific type.

        Use log_[type] instead.
        
        Arguments:
            name: str
            log_type: str
            category: str
            message: str
            bold: bool = False
            reversed: bool = False
            color: str = None
            placeholder_ext: dict = {}
        """

        # Make sure we should log this
        log = True
        if "script" in globals():
            if hasattr(script, "config"):
                if f"log_{category}" not in script.config.logging:
                    log = self.logging[category]

                else:
                    log = script.config.logging[f"log_{category}"]

        if not log:
            return

        # Verify log type exists
        if log_type not in self.log_types:
            raise exceptions.DevError(f"Log type {log_type} doesn't exist")

        # Get the color
        if color is None:
            color = self.log_types[log_type]

            if color.startswith("&"):
                color = f"\033[38;5;{color[1:]}m"

        if not color.startswith("\033"):
            color = self.colors[color]

        placeholders = {
            **self.get_placeholders(
                log_type,
                category,
                message,
                bold,
                color,
                reversed
            ),
            **placeholder_ext
        }

        msg = str(self.format[name])

        for placeholder, value in placeholders.items():
            msg = msg.replace(f"%{placeholder}%", str(value))

        scriptlib.terminal.log(
            msg,
            True
        )