import re
from pathlib import Path

from imxInsights import ImxSituationsEnum
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.validation import Failure, ValidationResult, Validator
from textual.widget import Widget
from textual.widgets import Label

from imxInsightsCli.imxDiffCli.generic import InputWithLabel, SelectWithLabel


class ImxFilePath(Widget):
    """An imx path and situation."""

    DEFAULT_CSS = """
    ImxFilePath {
        height: auto;
        border: solid blue;
    }
    ImxFilePath Label {
        width: 12;
        text-align: right;
    }
    ImxFilePath Input {
        width: 1fr;
    }
    #header_id_imx {
        width: 100%;
        text-align: center;
    }

    Horizontal {
        height: auto;
    }

    InputWithLabel {
        width: 70%;
    }

    SelectWithLabel{
        width: 30%;
    }

    """

    def __init__(self, imx_a_or_b: str) -> None:
        self.imx_a_or_b = imx_a_or_b
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(f"IMX file {self.imx_a_or_b}", id="header_id_imx")

        yield Horizontal(
            InputWithLabel("Imx path", validators=[XmlImxFileValidator()]),
            SelectWithLabel("Situation", [item for item in ImxSituationsEnum]),
        )


class XmlImxFileValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        """Check a imx path is value."""
        success = True
        fails = []

        if value == "":
            fails.append("Parameter cant be empty")
            success = False
        else:
            if not self.is_xml_extension(value):
                fails.append("File has no .xml extension")
                success = False

            if not self.file_exists(value):
                fails.append("File does not exist")
                success = False
            else:
                if not self.valid_imx_file(value):
                    fails.append("File is not valid IMX file")
                    success = False

        if success:
            return self.success()

        return ValidationResult(
            [Failure(validator=self, value=value, description=item) for item in fails],
        )

    @staticmethod
    def is_xml_extension(value: str) -> bool:
        if value.endswith(".xml"):
            return True
        return False

    @staticmethod
    def file_exists(value: str) -> bool:
        file_path = Path(value)
        if file_path.exists():
            return True
        return False

    @staticmethod
    def valid_imx_file(value: str) -> bool:
        file_path = Path(value)
        if file_path.exists():
            with open(value, "r", encoding="utf-8") as unknown_file:
                xml_string = unknown_file.read()
                if re.search(r"ImSpoor", xml_string) or re.search(r"IMSpoor", xml_string):
                    return True
        return False
