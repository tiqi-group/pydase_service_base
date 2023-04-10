from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class LogBroadcastMessageLevel(Enum):
    # low level messages that help tracking down issues
    DEBUG = "DEBUG"
    # generic messages
    INFO = "INFO"
    # something is suspicious, but program can continue normally
    WARNING = "WARNING"
    # something is wrong, correct program execution cannot be guaranteed
    ERROR = "ERROR"
    # program cannot continue to run any more
    CRITICAL = "CRITICAL"


class LogBroadcastMessage(BaseModel):
    originator: str = Field(
        ..., description="The script or service where this message comes from."
    )

    level: LogBroadcastMessageLevel = Field(
        ...,
        description="Log level of this message. Possible values: DEBUG, INFO, WARNING, CRITICAL",
    )
    message: str = Field(..., description="Actual content of the log message.")
    package: str = Field(
        ..., description="The python package where this message came from."
    )
    line_number: str = Field(
        ..., description="Line number where this message originated from."
    )
    function: str = Field(
        ..., description="The function that embeds the log message call."
    )
    timestamp: datetime = Field(..., description="When the log message was created.")

    @property
    def routing_key(self) -> str:
        """Routing key based on contents of this message.
        Constructed as: {self.__class__.__name__}.{self.level}.{self.package}"""
        return f"{self.originator}.{self.level}.{self.package}.{self.function}"
