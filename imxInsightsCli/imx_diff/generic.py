from typing import Optional, List

from textual import on
from textual.app import ComposeResult
from textual.containers import Horizontal
from textual.validation import Validator
from textual.widget import Widget
from textual.widgets import Pretty, Input, Label, Select


class InputWithLabel(Widget):
    """An input with a label."""

    DEFAULT_CSS = """
    Input.-valid {
        border: tall $success 60%;
    }
    Input.-valid:focus {
        border: tall $success;
    }
    Horizontal {
        height: auto;
    }
    InputWithLabel {
        layout: vertical;
        height: auto;
    }
    InputWithLabel Label {
        padding: 1;
        width: 12;
        text-align: right;
    }
    InputWithLabel Input {
        width: 1fr;
    }
    Pretty {
        padding-left: 14
    }
    """

    def __init__(self, input_label: str, id: str | None = None, optional: bool = False, validators: Optional[List[Validator]] = None) -> None:
        self.input_value = ""
        self.input_label = input_label
        self.optional = optional
        self.validators = validators
        self._label = Label(self.input_label)
        self._input = Input(validators=self.validators)

        super().__init__()
        if id is not None:
            self.id = id

    def compose(self) -> ComposeResult:
        if self.validators is not None:
            yield Horizontal(
                self._label,
                self._input
            )

        else:
            yield Horizontal(
                self._label,
                self._input
            )

        yield Pretty([])

    def on_mount(self) -> None:
        if not self.optional:
            self.query_one(Pretty).update("Parameter cant be empty")
        else:
            self.query_one(Pretty).update("Parameter is optional")

    @on(Input.Changed)
    def show_invalid_reasons(self, event: Input.Changed) -> None:
        if self.validators is not None:
            if not event.validation_result.is_valid:
                self.query_one(Pretty).update(event.validation_result.failure_descriptions)
            else:
                self.input_value = self._input.value
                self.query_one(Pretty).update([])


class SelectWithLabel(Widget):
    """A Select with a label."""

    DEFAULT_CSS = """
    Horizontal {
        height: auto;
    }
    SelectWithLabel {
        height: auto;
    }
    SelectWithLabel Label {
        padding: 1;
        width: 12;
        text-align: right;
    }
    SelectWithLabel Select {
        width: 0.8fr;
    }
    Pretty {
        padding-left: 14
    }
    """

    def __init__(self, input_label: str, options: List[str]) -> None:
        self.input_label = input_label
        self.options = options
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Horizontal(
            Label(self.input_label),
            Select([(option, option) for option in self.options], classes=self._classes, allow_blank=False)
        )
