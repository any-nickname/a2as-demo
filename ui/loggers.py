import re
import sys
import io

class GradioConsoleLogger(io.StringIO):
    def __init__(self):
        super().__init__()
        self.terminal = sys.stdout

    def write(self, message):
        self.terminal.write(message)
        super().write(message)