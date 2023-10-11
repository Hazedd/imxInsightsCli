import time
from pathlib import Path

from textual.app import App, ComposeResult
from textual.widgets import Markdown, Button, Footer, Header
from textual.containers import ScrollableContainer, Horizontal

from imxInsights import ImxSituationsEnum, Imx, ImxDiff, __version__ as imxInsightsVersion
from imxInsights.utils.shapely_geojson import dumps

from imxInsightsCli import __version__ as imxDiffCliVersion
from imxInsightsCli.imx_diff.imx import ImxFilePath, XmlImxFileValidator
from imxInsightsCli.imx_diff.ouput import OutputPath
from imxInsightsCli.imx_diff.scope_add import ExcelScope
from imxInsightsCli.imx_diff.uitwisselscope import UitwisselScopeExcelPath, ScopeExcelValidator


class ImxDiffApp(App):
    CSS = """
    Screen {
        align: center middle;
    }
    ScrollableContainer {
        # width: 190;
    }
    Button{
        width: 100%;
    }

    Markdown{
        width: 30%;
    }

    Toast {
        padding: 0;
        text-style: italic;
    }
    Markdown {
        height: auto;
    }
    """

    EXAMPLE_MARKDOWN = f"""
# Welcome to IMX Diff Version <<APP_VERSION>> using ImxInsights: <<BACKEND_VERSION>>!

IMX Diff CLI solution for comparing IMX files and generating comprehensive insights in Excel format. 
Additionally, this tool provides the ability to create GeoJSON files to document the differences between IMX datasets.

## when interested in a population, just diff same file, same situation 😉.

### IMX A and B:
- set the file path to the imx file. 
- select the situation to diff. 
- To copy a file path use "control + shift + v" 😊.

### Uitwisselscope:
- Optional we can map the uitwisselscope on the imx properties in the diff, we use a as-dataset sheet containing a path and a target.
    - the path is the elements route to the object of interest seen from the root (Situation).
    - the target is the attribute path seen from the path.
    - every other column is a scope and can contain True or False.
- when inputting the excel file all scopes will be listed and can be selected.
- flag for adding the selected scopes to the diff output.

### Output folder:
- set the output folder path where a folder called output will be created 
- overwriting is not implemented and disabled, make sure it's empty
- If kept empty the root of the application is the output folder. 


### Create diff excel
### Create diff geojsons


    """.replace("<<APP_VERSION>>", imxDiffCliVersion).replace("<<BACKEND_VERSION>>", imxInsightsVersion)

    def compose(self) -> ComposeResult:
        yield Header()
        yield Footer()
        # TODO: add header info text versions ect.
        # TODO: add root path as output folder on mount or here
        yield Horizontal(
            ScrollableContainer(
                ImxFilePath("A"),
                ImxFilePath("B"),
                UitwisselScopeExcelPath(),
                OutputPath(),
                Button("Create diff Excel", id="create_diff"),
                Button("Create diff geoJsons", id="create_geojson"),
            ),
            Markdown(self.EXAMPLE_MARKDOWN)
        )

    def on_button_pressed(self, event: Button.Pressed) -> None:

        if event.button.id in ["create_diff", "create_geojson"]:

            file_dict = {}
            errors = []
            warnings = []

            files = list(self.query(ImxFilePath))
            for file in files:
                result = XmlImxFileValidator().validate(
                    value=file.query_one("InputWithLabel Input").value
                )
                if len(result.failures) != 0:
                    errors.append(f"IMX {file.imx_a_or_b}: {' and '.join([item.description.lower() for item in result.failures])}")

                situation = file.query_one("SelectWithLabel Select").value
                if situation is None:
                    errors.append(f"IMX {file.imx_a_or_b}: does not have a selected situation")

                file_dict[file.imx_a_or_b] = {
                    "file": file.query_one("InputWithLabel Input").value,
                    "situation": situation
                }

            # todo: check if situations exist

            output_folder = self.query_one("#out_folder Input").value
            if output_folder == "":
                errors.append(f"Output path cant be empty!")

            overwrite = self.query_one("#overwrite").value
            out_path = Path(output_folder)
            if not out_path.is_dir():
                errors.append("output folder is not a directory")
            if out_path.exists() and any(out_path.iterdir()) and not overwrite:
                errors.append("output folder is not empty, set flag to overwrite if intended")

            uitwisselscope_path_validation = ScopeExcelValidator().validate(self.query_one("UitwisselScopeExcelPath InputWithLabel Input").value)
            if not uitwisselscope_path_validation.is_valid:
                for item in uitwisselscope_path_validation.failures:
                    errors.append(f"Uitwisselscope: {item.description}")

            proceed = True
            if len(errors) > 0:
                self.notify(
                    "\n".join([item for item in errors]),
                    title="ERROR", severity="error", timeout=10
                )
                proceed = False

            if len(warnings) > 0:
                self.notify(
                    "\n".join([item for item in warnings]),
                    title="WARNING", severity="warning", timeout=10
                )

            if proceed:

                output_folder = Path(f"{output_folder}\output")
                output_folder.mkdir(parents=True, exist_ok=True)

                imx_file_path_1 = file_dict["A"]["file"]
                imx_situation_1 = file_dict["A"]["situation"]
                imx_file_path_2 = file_dict["B"]["file"]
                imx_situation_2 = file_dict["B"]["situation"]
                imx = Imx(imx_file_path_1)
                if imx_file_path_1 == imx_file_path_2:
                    imx_old = imx
                else:
                    imx_old = Imx(imx_file_path_2)

                imx_situation_1 = imx.get_situation_repository(ImxSituationsEnum[imx_situation_1])
                imx_situation_2 = imx_old.get_situation_repository(ImxSituationsEnum[imx_situation_2])

                diff = ImxDiff(imx_situation_1, imx_situation_2)

                if event.button.id == "create_geojson":
                    geojson_dict = diff.generate_geojson_dict()

                    for key, value in geojson_dict.items():
                        geojson_out_path = Path(f"{output_folder}/geojosn/")
                        geojson_out_path.mkdir(parents=True, exist_ok=True)

                        with open(f"{geojson_out_path}/{key}.geojson", mode="w") as file:
                            file.write(dumps(value))

                    self.notify(
                        f"Created geojsons in {output_folder}",
                        title="SUCCESS", severity="information", timeout=10
                    )

                elif event.button.id == "create_diff":
                    diff.generate_excel(f"{output_folder}/_.xlsx")
                    temp_diff = Path(f"{output_folder}/_.xlsx")
                    file_name = f"diff-{time.strftime('%Y%m%d-%H%M%S')}.xlsx"

                    add_scope = self.query_one("UitwisselScopeExcelPath SelectWithLabel Select").value == "True"
                    if add_scope:
                        excel_path = self.query_one("UitwisselScopeExcelPath InputWithLabel Input").value
                        excel_scope = ExcelScope(Path(excel_path))
                        selected_scopes = self.query_one("UitwisselScopeExcelPath SelectionList").selected
                        excel_scope.add_scope(temp_diff, Path(f"{output_folder}/{file_name}"), selected_scopes)
                        temp_diff.unlink()
                    else:
                        temp_diff.rename(f"{output_folder}/{file_name}")

                    self.notify(
                        f"Created diff excel in {output_folder}",
                        title="SUCCESS", severity="information", timeout=10
                    )


if __name__ == "__main__":
    app = ImxDiffApp()
    app.run()