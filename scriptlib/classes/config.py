"""
scriptlib.classes.config

Class which stores all script config values.
Reads from a file, and expands everything into attributes.
"""

import aiofiles
import yaml
import json
import os
import inspect

from ..utils import (
    exceptions,
    colors
)

import scriptlib

from typing import Optional

class Config:
    def __init__(
            self
        ) -> None:
        pass

    async def init(
            self
        ) -> None:
        """
        Initalizes stuff & loads from file.
        
        Just a shortcut to load() at the moment.
        """

        await self.load()

    async def load(
            self,
            path: str = "config.yml"
        ) -> None:
        """
        Reads the config file.

        Arguments:
            path: str - Config file's path.
                Valid formats: yml, json
        """

        # Reserve some keywords
        self._sample_conf = None
        self._types_conf = None

        # Read file
        try:
            async with aiofiles.open(path, "r") as f:
                data = await f.read()

        except:
            # TODO: Read error, generate one
            raise exceptions.InitError(f"Config file does not exist at: '{path}'")

        if data is None:
            raise exceptions.InitError(f"Config file doesn't exist or couldn't be read.")

        # Find format
        final = path.strip("/").split("/")[-1]

        if "." not in final:
            raise exceptions.InitError(f"Path is invalid: Must have extension 'yml' or 'json'")

        # Get ext
        ext = final.split(".")[-1].lower()

        self._ext = ext

        try:
            if ext in ["yml", "yaml"]:
                parsed = yaml.safe_load(data)

            elif ext == "json":
                parsed = json.loads(data)

            else:
                raise exceptions.InitError(f"Invalid config file format: {ext}")

        except exceptions.InitError:
            raise

        except Exception as e:
            raise exceptions.InitError(f"Config value could not be read: {e}")

        if parsed is None:
            parsed = {}

        # Expand to attributes
        self._data = parsed

        for name, value in parsed.items():
            if hasattr(self, name):
                raise exceptions.InitError(f"Cannot override config option {name}.")

            setattr(self, name, value)

        # All good! Hand off to validator.
        await self.validate()

    async def validate(
            self
        ) -> None:
        """
        Validates config file against required types.
        """

        await self.load_templates()
        await self.validate_all()


    async def load_templates(
            self
        ) -> None:
        """
        Loads internal templates for config files,
        which are then used for validation.
        """

        # Read based on format
        path = f"{os.path.dirname(inspect.getfile(scriptlib))}/config/"
        sample_path = f"{path}config.sample.{self._ext}"
        types_path = f"{path}config.types.yml"

        # Load up sample
        if not os.path.exists(sample_path):
            raise exceptions.InitError(f"No sample config exists for type {self._ext}.")

        async with aiofiles.open(sample_path, "r") as f:
            self._sample_conf = await f.readlines()

        # Load up and parse types
        if not os.path.exists(types_path):
            raise exceptions.InitError(f"No type definitions exist for config.", traceback = False)

        async with aiofiles.open(types_path, "r") as f:
            data = await f.read()

        # Parse from YAML - samples will all use this, regardless of type.
        self._types_conf = yaml.safe_load(data)

    async def validate_all(
            self
        ) -> None:
        """
        Validates all config values.
        """

        # Iterate over types definition, since this includes all
        # required config opts
        for name, rule in self._types_conf.items():
            # Check exists
            if not hasattr(self, name):
                await self.invalid_conf(f"Missing key '{name}'.", opt = name)
                
            value = getattr(self, name)

            # Check with arg parser
            if type(value) == str:
                # Check regularly, in case it's a type that doesn't exist in YAML or JSON.
                valid, result = await scriptlib.script.args.parse(
                    rule,
                    str(value),
                    {}
                )

            else:
                # Assume it's a pre-typed value.
                valid, result = await scriptlib.script.args.parse_typed(
                    rule,
                    value,
                    {}
                )

            if not valid:
                await self.invalid_conf(f"Validation failed for '{name}': {', '.join(result)}", opt = name, rule = rule)

            # Store
            #setattr(self, name, value)
            # Disabling for now. Could solve problems with YAML being funky later, but this is more hacky than I'd like.

            
    async def invalid_conf(
            self,
            message: str,
            opt: Optional[str] = None,
            rule: Optional[str] = None
        ) -> None:
        """
        Sends a configuration error to the terminal,
        then raises a non-fatal InitError. Optionally
        shows a sample of the config opt, and what the
        arg validator is looking for.
        
        Arguments:
            message: str - Error message to display
            opt: Optional[str] - Config option that's invalid
            rule: Optional[str] - Argval rule for config option
        """

        # Log main stuff
        scriptlib.script.logger.log(
            "error",
            "init",
            "A config error occurred!",
            True
        )
        scriptlib.script.logger.log_step(
            "error",
            "init",
            message
        )

        # Check if the opt is set - if so, log that
        if opt:
            sample = self.get_sample(opt)

            if sample is not None:
                # Log the sample, if it exists

                scriptlib.t.log(" ")
                
                scriptlib.script.logger.log(
                    "error",
                    "init",
                    "Here's a sample for this config option:",
                    bold = True
                )

                scriptlib.script.logger.log_long(
                    "error",
                    "init",
                    sample,
                )

        raise exceptions.InitError("Configuration error encountered.", False, False)

    def get_sample(
            self,
            opt: str
        ) -> list:
        """
        Gets a config sample for an option.
        
        Arguments:
            opt: str - Option to find
            
        Returns:
            sample: list - Sample string, split into a list of lines
        """

        locators = {
            "yml": self.sample_yml,
            "yaml": self.sample_yml,
            "json": self.sample_json
        }

        return locators[self._ext](opt)

    def sample_yml(
            self,
            opt: str
        ) -> list:
        """
        Gets a YML sample for a config option.

        Use self.get_sample() instead.
        
        Arguments:
            opt: str
            
        Returns:
            sample: list
        """

        # Iterate over sample
        for i, line in enumerate(self._sample_conf):
            if line.startswith(f"{opt}:"):
                # Found the var. Now search for everything before & after
                comp = []

                # Look for comments above
                active = self._sample_conf[i - 1]
                active_i = i - 1

                while active.startswith("#"):
                    comp.append(active.strip())
                    active_i -= 1
                    
                    if active_i < 0:
                        active = ""

                    else:
                        active = self._sample_conf[active_i]

                # Reverse this, since it's backwards
                comp.reverse()

                # Add the actual line
                comp.append(f"{colors.TerminalColors.BOLD}{line.strip()}")

                # Find every tabbed line after
                active = self._sample_conf[i + 1]
                active_i = i + 1

                while active.startswith(" ") or (active.strip() == "" and self._sample_conf[active_i + 1].startswith(" ")):
                    comp.append(active)

                    active_i += 1
                    if active_i > len(self._sample_conf) - 1:
                        active = ""

                    else:
                        active = self._sample_conf[active_i]

                # Send back value
                return comp

    def sample_json(
            self,
            opt: str
        ) -> list:
        """
        Gets a JSON sample for a config option.

        Use self.get_sample() instead.
        
        Arguments:
            opt: str
            
        Returns:
            sample: list
        """

        return ["JSON config samples aren't set up yet."]