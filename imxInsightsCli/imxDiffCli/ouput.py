from pathlib import Path

from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.validation import Failure, ValidationResult, Validator
from textual.widget import Widget
from textual.widgets import Label, Static, Switch

from imxInsightsCli.imxDiffCli.generic import InputWithLabel


class OutputPath(Widget):
    DEFAULT_CSS = """
    OutputPath {
        height: auto;
        border: solid purple;
    }

    OutputPath Label {
        width: 12;
        text-align: right;
    }

    OutputPath Input {
        width: auto;
    }

    Horizontal {
        height: auto;
    }

    Switch {
        height: auto;
        width: auto;
    }

    .label {
        height: 3;
        content-align: center middle;
        width: auto;
    }

    #header_id_output {
        width: 100%;
        text-align: center;
    }
    """

    def __init__(self) -> None:
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label("Output", id="header_id_output")

        yield Horizontal(
            Horizontal(
                InputWithLabel("output folder", id="out_folder", validators=[OutputPathValidator()]),
            ),
            Static("overwrite:", classes="label"),
            Switch(value=True, id="overwrite", disabled=True),
        )


class OutputPathValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        """Check if value is valid folder."""
        success = True
        fails = []

        if value == "":
            fails.append("Parameter cant be empty")
            success = False
        else:
            if not self.is_directory(value):
                fails.append("Path is no directory")
                success = False

            if self.is_system_root(value):
                fails.append("Path cant be system root")
                success = False

        if success:
            return self.success()

        return ValidationResult(
            [Failure(validator=self, value=value, description=item) for item in fails],
        )

    @staticmethod
    def is_directory(value: str) -> bool:
        if Path(value).is_dir():
            return True
        return False

    @staticmethod
    def is_system_root(value: str):
        absolute_path = Path(value).absolute()
        if absolute_path == Path(absolute_path.anchor):
            return True
        return False
