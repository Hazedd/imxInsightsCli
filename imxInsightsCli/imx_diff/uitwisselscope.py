from pathlib import Path
from typing import Optional

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.validation import ValidationResult, Failure, Validator
from textual.widget import Widget
from textual.widgets import Input, Select, Label, SelectionList

from imxInsightsCli.imx_diff.generic import SelectWithLabel, InputWithLabel
from imxInsightsCli.imx_diff.scope_add import ExcelScope


class UitwisselScopeExcelPath(Widget):
    """An excel uitwisselscope input."""

    # todo: implement imx path validation on path and extension, maybe present of as-dataset and info sheet?

    DEFAULT_CSS = """
    UitwisselScopeExcelPath {
        height: auto;
        border: solid red;
    }
    UitwisselScopeExcelPath Label {
        width: 12;
        text-align: right;
    }
    UitwisselScopeExcelPath Input {
        width: auto;
    }

    InputWithLabel {
        width: 80%;
    }

    SelectWithLabel{
        width: 20%;
    }

    Horizontal {
        height: auto;
    }

    #header_id_uitwisselscope {
        width: 100%;
        text-align: center;
    }
    """

    def __init__(self) -> None:
        self._excel_scope: Optional[ExcelScope] = None
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label(" Uitwisselscope", id="header_id_uitwisselscope")
        yield Horizontal(
            InputWithLabel("Excel path", optional=True, validators=[ScopeExcelValidator()]),
            SelectWithLabel("add scope", ["True", "False"])
        )
        yield SelectionList[int](
            ("missing excel path", "missing", False)
        )

    @on(Select.Changed)
    def add_scope_changed(self, message: Select.Changed):
        add_scope = self.query_one("SelectWithLabel Select").value == 'True'
        if add_scope:
            if not ScopeExcelValidator().validate(self.query_one("InputWithLabel Input").value).is_valid:
                self.query_one("InputWithLabel Pretty").update("Parameter cant be empty")
        else:
            try:
                self.query_one("InputWithLabel Pretty").update(self._excel_scope.scope_version)
            except:
                self.query_one("InputWithLabel Pretty").update("Parameter is optional")

    def on_input_changed(self, message: Input.Changed) -> None:
        if ScopeExcelValidator().validate(self.query_one("InputWithLabel Input").value).is_valid:
            uitwisselscope_input_value = self.query_one("InputWithLabel Input").value
            excel_path = Path(uitwisselscope_input_value)
            try:
                self._excel_scope = ExcelScope(excel_path)
                self.query_one("InputWithLabel Pretty").update(self._excel_scope.scope_version)
                scopes = [item for item in list(self._excel_scope.df_scope.columns) if item not in ["path", "target"]]
                scopes = [(item, item, False) for item in scopes]
                selection_list = self.query_one("SelectionList")
                selection_list.clear_options()
                selection_list.add_options(scopes)
            except Exception as e:
                self.query_one("InputWithLabel Pretty").update(f"File is not a valid uitwisselscope excel")
                self.query_one("SelectionList").clear_options()
                self._excel_scope = None
        else:
            self.query_one("SelectionList").clear_options()
            self._excel_scope = None


class ScopeExcelValidator(Validator):
    def validate(self, value: str) -> ValidationResult:
        """Check a imx path is value."""

        success = True
        fails = []

        if value == "":
            fails.append("Parameter cant be empty")
            success = False
        else:
            if not self.is_xlsx_extension(value):
                fails.append("File has no .xlsx extension")
                success = False

            if not self.file_exists(value):
                fails.append("File does not exist")
                success = False

        if success:
            return self.success()

        return ValidationResult(
            [Failure(validator=self, value=value, description=item) for item in fails],
        )

    @staticmethod
    def is_xlsx_extension(value: str) -> bool:
        if value.endswith(".xlsx"):
            return True
        return False

    @staticmethod
    def file_exists(value: str) -> bool:
        file_path = Path(value)
        if file_path.exists():
            return True
        return False
