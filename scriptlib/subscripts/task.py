"""
scriptlib.subscripts.task
(scriptlib.subscripts.TaskScript)

"""

from typing import Iterable, Optional
import asyncio

from scriptlib.utils import (
    exceptions,
    errorhandler
)

from scriptlib.classes.subscript import (
    Subscript
)

class TaskSubscript(Subscript):
    """
    Task-based subscript.
    
    Runs a number of functions sequentially. Define them with
    self.tasks, or self.add_tasks(*tasks) if not being
    extended.
    
    Sample task:
        {
            "name": "Sample task",
            "description": "Does something, maybe." # Optional. But don't be lazy and define this.
            "function": self.sample_task, # Async function
            "if": lambda subscript: subscript.some_value == 3 # Optional. Self is passed, use a lambda statement. Will only run if True.
        }
    """
    def __init__(
            self,
            *tasks,
            **kwargs
        ) -> None:
        """
        Initializes the object.
        """

        super().__init__(**kwargs)

        # Define task structure.
        self.req = { # TODO: Use arg parser
            "name": lambda val: type(val) == str,
            "description": lambda val: type(val) == str,
            "function": lambda val: asyncio.iscoroutinefunction(val)
        }

        self.opt = {
            "if": lambda val: callable(val)
        }

        self.tasks = {}

        if len(tasks) > 0:
            self.add_tasks(*tasks)

        global script
        from scriptlib import script

    def validate_task(
            self,
            task: dict
        ) -> bool:
        """
        Validates a task.
        
        Arguments:
            task: dict - Task to validate
            
        Returns:
            valid: bool - Valid or not
            reason: Optional[str] - If invalid, why
        """

        # Verify type
        if type(task) != dict:
            return False, "Task is not a dict"

        # Check and validate required keys
        for name, check in self.req.items():
            if name not in task:
                return False, f"Missing required key {name}"

            if not check(task[name]):
                return False, f"Value of {name} failed validation check"

        # Check for optional keys
        for name, check in self.opt.items():
            if name not in task:
                continue

            if not check(task[name]):
                return False, f"Value of {name} failed validation check"

        # Remove duplicates
        if task["name"].lower() in self.tasks:
            return False, f"Task {task['name'].lower()} is already registered"

        # All set!
        return True, None

    def add_tasks(
            self,
            *tasks
        ) -> None:
        """
        Adds a number of tasks to the register.
        
        Arguments:
            *tasks: dict - Tasks to add.
            Sample task:
                {
                    "name": "Sample task",
                    "description": "Does something, maybe." # Optional. But don't be lazy and define this.
                    "function": self.sample_task, # Async function
                    "if": lambda subscript: subscript.some_value == 3 # Optional. Self is passed, use a lambda statement. Will only run if True.
                }
        """

        for task in tasks:
            # Validate
            valid, reason = self.validate_task(
                task
            )

            if not valid:
                raise exceptions.DevError(f"Invalid task {task.get('name') if type(task) == dict else 'None'}: {reason}")

            self.tasks[task["name"]] = task

    async def run(
            self
        ) -> Optional[int]:
        """
        Runs all the tasks.
        
        Returns:
            status_code: Optional[int] - Status code, if tasks returned any.
        """

        for i, (name, task) in enumerate(self.tasks.items()):
            # Log it
            script.logger.log("info", "subscript", f"Running task {task['name']}: {task['description']} ({i + 1}/{len(self.tasks)})")

            # Do it
            res = await errorhandler.wrap(
                task['function']()
            )

            if not res:
                # Error occurred -- exit
                script.logger.log("error", "subscript", f"An error occurred while executing task {task['name']}. Exiting subscript.")
                return