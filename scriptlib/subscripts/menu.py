"""
scriptlib.subscripts.task
(scriptlib.subscripts.TaskScript)

"""

from typing import List

from scriptlib.classes.subscript import (
    Subscript
)

from scriptlib.utils import (
    errorhandler
)

import scriptlib

class MenuSubscript(Subscript):
    """
    Menu for other scripts.

    Make sure to add 'self.run = False' to any subscripts
    added to the menu, or add the menu script first.
    """

    def __init__(
            self,
            subscripts: List[Subscript],
            dialog: str = "Menu",
            run_forever: bool = False
        ) -> None:
        self.subscripts = subscripts

        # Disable auto-run on all subscripts
        for subscript in self.subscripts:
            subscript.auto_run = False

        self.dialog = dialog

        self.run_forever = run_forever


        global script
        from scriptlib import script

    async def run(
            self
        ) -> None:
        """
        Display the menu.
        """
        # Print menu name
        script.logger.log("ask", "menu", f"-- {self.dialog} -- ", bold = True)

        # Print each option
        for i, subscript in enumerate(self.subscripts):
            script.logger.log_step("ask", "menu", f"{i + 1} | {subscript.name} | {subscript.description}")

        num = None
        while not num:
            # Ask for result
            scriptnum = await scriptlib.terminal.ask("Which script would you like to run?", "#", "Enter a script number here and press enter.")

            # Try to parse to an int
            valid, res = await script.args.parse(
                f"int[between(1,{len(self.subscripts)}",
                scriptnum,
                {}
            )

            if not valid:
                script.logger.log("error", "menu", f"Invalid script number '{scriptnum}'. Try again.")

            else:
                num = res

        sel_script = self.subscripts[num - 1]

        # Run script
        script.logger.log("ask", "menu", f"Running script {num}: {sel_script.name}")
        script.logger.log_step("ask", "menu", sel_script.description)

        await errorhandler.wrap(
            sel_script.run()
        )

        if self.run_forever:
            await self.run()