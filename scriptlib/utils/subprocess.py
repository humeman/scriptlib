"""
scriptlib.utils.subprocess

Contains a number of functions and classes for running
shell commands.
"""

import asyncio
import shlex
import subprocess

from . import (
    exceptions
)

import scriptlib

def sync_run(command):
    subprocess.call(command, shell = True)

def get_output(command):
    return subprocess.check_output(shlex.split(command))

async def run(command):
    cmd = Command(command)

    await cmd._init()

    return cmd

class Command:
    def __init__(
            self, 
            command
        ) -> None:
        self.command = command
        
        self.process = None
        self.task = None

        self.data = []

    @property
    def result(self) -> str:
        """
        Gets a joined version of the task's current
        stdout.
        
        Returns:
            result (str)
        """
        return "".join(self.data)

    async def _init(
            self
        ) -> None:
        """
        Asynchronously initializes and runs a command.
        """
        self.process = await asyncio.create_subprocess_shell(
            self.command,
            stdin = asyncio.subprocess.PIPE,
            stdout = asyncio.subprocess.PIPE,
            stderr = asyncio.subprocess.STDOUT
        )

        scriptlib.loop.create_task(self.handle_stdout())

        await self.process.wait()

        if self.process.returncode != 0:
            # TODO: Implement logging
            # logger.log("subprocess", "error", f"Subprocess call for '{self.command}' returned non-zero exit code: {self.process.returncode}")
            raise exceptions.SubprocessError(self.process.returncode)

    async def kill(
            self
        ) -> None:
        """
        Prematurely kills the running task.
        """
        self.process.terminate()
    
    async def handle_stdout(
            self
        ) -> None:
        """
        Handles output of the command.
        """
        while not self.process.returncode:
            # Process is still running
            try:
                msg = await self.process.stdout.readuntil(b"\n")
                data = msg.decode("ascii").rstrip()

                self.data.append(data)

                # We will eventually log this
                #terminal.log_raw("subprocess", "info", data, True)
                scriptlib.terminal.log(f"> {data}", True)

            except asyncio.IncompleteReadError:
                break
                #logger.log("warn", "Subprocess exited while reading.")

            except asyncio.LimitOverrunError:
                # Shouldn't happen yet.
                # TODO
                #humecord.logger.log("subprocess", "warn", "Subprocess limit overrun. Can't read data.")
                pass

            except:
                #humecord.logger.log("subprocess", "error", "Failed to read data from subprocess.")
                pass