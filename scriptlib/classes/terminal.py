
import blessed
import os
import signal
import re
from typing import Optional
import termios
import tty

from scriptlib.utils import (
    colors
)


ansi_escape = re.compile(r'''
    \x1B  # ESC
    (?:   # 7-bit C1 Fe (except CSI)
        [@-Z\\-_]
    |     # or [ for CSI, followed by a control sequence
        \[
        [0-?]*  # Parameter bytes
        [ -/]*  # Intermediate bytes
        [@-~]   # Final byte
    )
''', re.VERBOSE)
class Terminal:
    """
    Class which stores all terminal information and methods.
    
    Note that the entire terminal is run synchronously in another thread.
    """

    def __init__(
            self
        ) -> None:
        # We have to call init stuff later to prevent circular imports.
        pass

    def init(
            self
        ) -> None:
        """
        Actual initialization function.
        """
        global Console
        from .console import Console
        
        self.term = blessed.Terminal()

        # Start stuff
        tty.setcbreak(self.term._keyboard_fd, termios.TCSANOW)
        print(self.term.enter_fullscreen + self.term.clear + self.term.clear)

        self.lines = []
        self.title = "Test"
        self.line_numbers = True

        self.location = 0
        self.manual_scroll = False

        self.colors = {
            "border": "green",
            "info": "cyan",
            "secondary": "dark_gray",
            "console": "blue",
            "ask": "magenta"
        }

        self.borders = {
            Border.NONE: ["│", " ", "│"],
            Border.TOP: ["┌", "─", "┐"],
            Border.MIDDLE: ["├", "─", "┤"],
            Border.BOTTOM: ["└", "─", "┘"]
        }

        signal.signal(signal.SIGWINCH, self.update_size)

        self.expand_colors()
        self.console = Console()

        self.update_size() # Start!

    def expand_colors(
            self
        ) -> None:
        """
        Expands self.colors into ANSI color codes.
        """

        self.color = {}
        
        for name, val in self.colors.items():
            self.color[name] = colors.termcolors[val]

    def update_size(
            self,
            *args
        ) -> None:
        """
        Updates and reprints the terminal based on col/row size
        changes.
        """

        if not self.manual_scroll and hasattr(self, "log_count"):
            self.location = len(self.lines) - self.log_count

            if self.location < 0:
                self.location = 0

        self.log_count = self.term.height - 7

        self.reprint(True)

    def reprint(
            self,
            all: bool = False,
            title: bool = False,
            logs: bool = False,
            console: bool = False
        ) -> None:
        """
        Reprints the specified terminal sections.
        
        Arguments:
            all: bool - Redraw everything
            title: bool - Redraw title box
            logs: bool - Redraw log section
            console: bool - Redraw console box
        """

        if all:
            print(self.term.clear, end = "")

        actions = {
            self.draw_box: False or all,
            self.print_title: title or all,
            self.print_logs: logs or all,
            self.print_console: console or all
        }
        
        for func, do in actions.items():
            if do:
                func()

    def log(
            self,
            message: str,
            update: bool = False
        ) -> None:
        """
        Logs a message to the terminal.
        
        Arguments:
            message: str - Message to log
            update: bool - Automatically redraw
        """

        self.lines.append(message)

        # TODO: Log to file

        self.adjust_scroll()

        if update:
            self.reprint(logs = True)

    def getch(
            self,
            timeout: float = 0.02
        ) -> Optional[str]:
        """
        Waits for character input until the specified timeout.
        
        Arguments:
            timeout: float - Time to wait for until returning None.
            
        Returns:
            char: str, None - Character returned.
        """

        return self.term.inkey(timeout = timeout)

    def adjust_scroll(
            self
        ) -> None:
        """
        Scrolls to the bottom if manual scroll is on
        (ie: scrolled to bottom, then new message logged)
        """

        if not self.manual_scroll:
            self.location = len(self.lines) - self.log_count

            if self.location < 0:
                self.location = 0

    def scroll(
            self,
            diff: int
        ) -> None:
        """
        Scrolls the terminal.
        
        Arguments:
            diff: int - Lines to scroll by.
        """

        max_scroll = len(self.lines) - self.log_count + 1

        new = self.location + diff

        # Check if scrolling beyond bottom
        if new >= max_scroll:
            self.manual_scroll = False
            return

        # Check if trying to scroll beyond top
        if new < 0:
            return

        self.location = new

        # Check if at bottom
        if self.location >= max_scroll:
            # Set to max
            self.location = max_scroll
            self.manual_scroll = False

        # Otherwise, don't autoscroll on new line
        else:
            self.manual_scroll = True

        self.adjust_scroll()

        self.reprint(logs = True)

    def shutdown(
            self
        ) -> None:
        """
        Cleans up everything and stops printing.
        """
        self.console.shutdown = True
        os.system("stty sane")
        print(self.term.exit_fullscreen + self.term.clear + self.term.home)

    # -- DRAW FUNCTIONS --
    def draw_box(
            self
        ) -> None:
        """
        Draws the outline/border of the window.
        """

        # Our sections are at:
        # Lines 1, 3 and height - 3, height - 1
        lines = {
            1: Border.TOP,
            3: Border.MIDDLE,
            self.term.height - 3: Border.MIDDLE,
            self.term.height - 1: Border.BOTTOM 
        }

        for line, border in lines.items():
            self.draw_border_line(line, border)

        # Draw the box - or, fill in everything else with Border.NONE.
        for line in [2, self.term.height - 2] + list(range(4, self.term.height - 3)):
            self.draw_border_line(line, Border.NONE)

    def draw_border_line(
            self,
            line: int,
            border_type: int
        ) -> None:
        """
        Draws one line of the window border.

        Arguments:
            line: int - Line number to draw at
            border_type: Border - Border segment to draw
        """

        # Generate string
        border = self.borders[border_type]

        # Ew
        line_str = f"{self.color['border']}{border[0]}{colors.TerminalColors.RESET if border[1] == ' ' else ''}{border[1] * (self.term.width - 2)}{self.color['border']}{border[2]}{colors.TerminalColors.RESET}"

        with self.term.location(0, line):
            print(line_str, end = "")

    # -- PRINT FUNCTIONS --
    def print_title(
            self
        ) -> None:
        """
        Prints the actual title text to the top bar.
        """

        with self.term.location(2, 2):
            print(self.center(f"{self.color['info']}{colors.TerminalColors.BOLD}{self.title}{colors.TerminalColors.RESET}"), end = "")

    def print_console(
            self
        ) -> None:
        """
        Draws out the bottom console line.
        """

        with self.term.location(2, self.term.height - 2):
            # 3 modes:
            # - Regular mode
            # - Ask mode
            # - Menu mode
            if self.console.mode == ConsoleModes.REGULAR:
                form = f"{self.color['console']}{colors.TerminalColors.BOLD}${colors.TerminalColors.RESET} {self.color['console']}{self.console.current[ConsoleModes.REGULAR]}{colors.TerminalColors.RESET}"


            elif self.console.mode == ConsoleModes.ASK:
                form = f"{self.color['ask']}{colors.TerminalColors.BOLD}>{colors.TerminalColors.RESET} {self.color['ask']}{self.console.current[ConsoleModes.ASK]}{colors.TerminalColors.RESET}"

            else:
                raise NotImplementedError()
                #form = f"{self.color['ask']}{colors.TerminalColors.BOLD}{self.console.current['menu']['id'] + 1}"

            # Pad with spaces to clear old stuff
            form += " " * (self.term.width - 5 - len(re.sub(ansi_escape, "", form)))

            print(form, end = "")

        print(self.term.move_xy(4 + self.console.location, self.term.height - 2))

        # Move cursor to console location
        #self.log(str(self.console.location), True)
        #print(self.term.move_xy(4 + self.console.location, self.term.height - 2), end = "")#, end = "")

    def print_logs(
            self
        ) -> None:
        """
        Prints out all stored logs.
        """

        # Generate scrollbar
        scrollbar = self.generate_scrollbar()

        line_count = len(self.lines)
        for i in range(0, self.term.height - 7):
            location = i + 4
            line_index = i + self.location

            if line_index < line_count:
                with self.term.location(2, location):
                    line = self.lines[line_index].replace("\t", "    ")

                    line_numbers = False
                    if self.term.width < 80:
                        line = line.strip()

                    else:
                        line_numbers = True

                    ext = ""

                    if self.line_numbers and line_numbers:
                        if line.strip() != "":
                            ext = f"{self.color['secondary']}{line_index + 1} "
                            line_numbers = True

                    stripped = re.sub(ansi_escape, "", line)

                    bounds = self.term.width - 3 - (2 if line_numbers else 0) - len(ext) + (len(line) - len(stripped))

                    print(" " * self.term.height, self.term.move_x(2), end = "")

                    print(f"{ext}{line[:bounds]}{self.term.move_x(self.term.width - 3)}{self.color['info']}{scrollbar[i]}{colors.TerminalColors.RESET}", end = "")

    def generate_scrollbar(
            self
        ) -> str:
        """
        Generates a scrollbar string based on
        the current location and number of lines.
        
        Returns:
            scrollbar: str
        """

        block = "█"
        empty = "░"

        height = self.term.height - 7

        # Find out section of terminal we're viewing
        lines = len(self.lines)
        if lines == 0:
            line_len = 1

        else:
            line_len = lines

            if line_len == 0:
                line_len = 1

        percent = height / line_len

        if percent > 1:
            percent = 1

        # Multiply by height to find total char count
        chars = int(percent * height)

        if chars == 0:
            chars = 1

        # Find term location by percent
        location_percent = self.location / line_len

        # Scale it to the total line count to get a location
        bar_start = int(location_percent * height)

        # Compile to a string
        bar = f"{empty * bar_start}{block * (chars + 1)}{empty * (height - bar_start - chars - 1)}"

        if len(bar) < line_len:
            bar += (empty * (len(bar) - line_len))

        return bar

    def center(
            self,
            message: str
        ) -> str:
        """
        Centers the text, ignoring ANSI codes, based on
        the width of the terminal.

        Arguments:
            message: str - Message to center

        Returns:
            message: str - Centered message
        """

        stripped = len(re.sub(ansi_escape, "", message))

        message = message[:self.term.width - 4 + len(message) - stripped]

        padding = ((self.term.width - 4) - stripped) // 2

        return f"{' ' * padding}{message}{' ' * padding}"

        





class Border:
    NONE = 0    # |      |
    TOP = 1     # |******|
    MIDDLE = 2  # |------|
    BOTTOM = 3  # |______|

class ConsoleModes:
    REGULAR = 0
    ASK = 1
    MENU = 2