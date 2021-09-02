
import blessed

import os
import asyncio
import signal

from scriptlib.utils import (
    colors
)

class Terminal:
    """
    Class which stores all terminal information and methods.
    
    Note that the entire terminal is run synchronously in another thread.
    """

    def __init__(
            self
        ) -> None:
        self.term = blessed.Terminal()

        # Start stuff
        print(self.term.enter_fullscreen + self.term.clear + self.term.clear)

        self.lines = []

        self.manual_scroll = True

        self.colors = {
            "border": "green",
            "info": "cyan",
            "secondary": "dark_gray",
            "terminal": "blue"
        }

        self.borders = {
            Border.NONE: ["│", " ", "│"],
            Border.TOP: ["┌", "─", "┐"],
            Border.MIDDLE: ["├", "─", "┤"],
            Border.BOTTOM: ["└", "─", "┘"]
        }

        signal.signal(signal.SIGWINCH, self.update_size)

        self.expand_colors()

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

        actions = {
            self.draw_box: False or all,
            #self.draw_title: title or all,
            #self.draw_logs: logs or all,
            #self.draw_console: console or all
        }
        
        for func, do in actions.items():
            if do:
                func()

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

    def shutdown(
            self
        ) -> None:
        """
        Cleans up everything and stops printing.
        """

        print(self.term.exit_fullscreen + self.term.clear + self.term.home)
        os.system("stty sane")



class Border:
    NONE = 0    # |      |
    TOP = 1     # |******|
    MIDDLE = 2  # |------|
    BOTTOM = 3  # |______|