from __future__ import annotations
import subprocess, os, platform
import time
from pathlib import Path
from collections import OrderedDict

from imxInsights.domain.imx import Imx


from imxInsights import __version__ as backend_version, ImxSituationsEnum, ImxDiff

app_version = "0.0.3-alpha5"

from rich.console import Console, Text

from consolemenu import MenuFormatBuilder, ConsoleMenu
from consolemenu.items import FunctionItem, SubmenuItem, CommandItem
from consolemenu.menu_component import Dimension


from ruamel.yaml import YAML

# rich, console-menu, pyinstaller
# todo: make option in cli to add scope excel.
# todo: build cli app in pipeline and share as artifact in release.
# todo: make test so cli app is working when building
# pyinstaller imx_to_excel.py --onefile

console = Console(width=100)

style_warning = "bold white on red"
question_style = "bold white on magenta"
info_style = "bold white on blue"


def get_yaml_dict(file_path):
    yaml = YAML()
    yaml.default_flow_style = True
    with open(file_path, "r") as stream:
        return yaml.load(stream)


def save_dict_as_yaml(data, out_file_path):
    yaml = YAML()
    # yaml.default_flow_style = True
    with open(out_file_path, "w") as outfile:
        yaml.dump(data, outfile)


settings_yaml_path = "app_settings.yaml"
config_yaml = get_yaml_dict(settings_yaml_path)
if config_yaml:
    imx_file_path_1 = config_yaml["imx_file_path_1"]
    imx_situation_1 = config_yaml["imx_situation_1"]
    imx_file_path_2 = config_yaml["imx_file_path_2"]
    imx_situation_2 = config_yaml["imx_situation_2"]
    output_path = config_yaml["output_path"]
else:
    imx_file_path_1 = r""
    imx_situation_1 = r"."
    imx_file_path_2 = r""
    imx_situation_2 = r"."
    output_path = r""


def menu_save_settings():
    global imx_file_path_1, imx_situation_1, imx_file_path_2, imx_situation_2, output_path, settings_yaml_path

    config_yaml = OrderedDict()
    config_yaml["imx_file_path_1"] = imx_file_path_1
    config_yaml["imx_situation_1"] = imx_situation_1
    config_yaml["imx_file_path_2"] = imx_file_path_2
    config_yaml["imx_situation_2"] = imx_situation_2
    config_yaml["output_path"] = output_path

    save_dict_as_yaml(config_yaml, settings_yaml_path)

    pass


def root_menu_title() -> str:
    return "Imx to diff excel."


def root_menu_subtitle() -> str:
    return f"Can be used to compare 2 imx situations. Just interested in the population diff it to itself.\nApp version: v{app_version}, backend imxInsights v{backend_version}"


def menu_prologue_text():
    global imx_file_path_1, imx_file_path_2, imx_situation_1, imx_situation_2, output_path
    return f"IMX file 1: \t   {imx_file_path_1} \nsituation file 1:  {imx_situation_1}\nIMX file 2: \t   {imx_file_path_2}\nsituation file 2:  {imx_situation_2}\nOutput dir: \t   {output_path}"


def get_about_menu(menu_formatter):
    help_text = "help is still a todo\n.\nFeature roadmap:\n - add vba to excel for formatting create, deleted and changed.\n - add vba to excel for puic ref navigation.\n.\n"

    # todo: get from LICENSE.MD
    license_text = 'MIT License, Copyright (c) 2023-2033 ProRail - IDE \n\nThe above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.\n\nTHE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.'

    return ConsoleMenu(f"{help_text}\n{license_text}", formatter=menu_formatter)


def menu_check_path_exist(file_path):
    if os.path.exists(f"{file_path}"):
        return True
    console.print(f"file path is not valid", style=style_warning, justify="left")
    time.sleep(3)
    return False


def menu_check_situation_is_valid(situation):
    if situation in [e.value for e in ImxSituations]:
        return True
    console.print(f"situation is not valid", style=style_warning, justify="left")
    time.sleep(3)
    return False


def menu_set_imx_file_1():
    global imx_file_path_1

    file_path = console.input(Text("What is the imx file path for file 1?\n", style=question_style))
    file_path = menu_clean_path_string(file_path)
    if menu_check_path_exist(file_path):
        imx_file_path_1 = file_path


def menu_set_imx_file_2():
    global imx_file_path_2

    file_path = console.input(Text("What is the imx file path for file 2?\n", style=question_style))
    file_path = menu_clean_path_string(file_path)
    if menu_check_path_exist(file_path):
        imx_file_path_2 = file_path


def menu_situation_pick_list():
    print(f"Select a imx situation to diff, possible situations:")
    pick_list = {}
    for idx, item in enumerate([e.value for e in ImxSituationsEnum]):
        print(f"\t {str(idx +1)}: {item}")
        pick_list[str(idx + 1)] = item
    return pick_list


def menu_set_imx_1_situation():
    global imx_situation_1

    pick_list = menu_situation_pick_list()
    number = console.input(Text("What is the imx situation for file 1?\n", style=question_style))
    situation = pick_list[number]
    if menu_check_situation_is_valid(situation):
        imx_situation_1 = situation


def menu_set_imx_2_situation():
    global imx_situation_2

    pick_list = menu_situation_pick_list()
    number = console.input(Text("What is the imx situation for file 2?\n", style=question_style))
    situation = pick_list[number]
    if menu_check_situation_is_valid(situation):
        imx_situation_2 = situation


def menu_clean_path_string(path):
    if len(path) != 0 and path[0] == '"' and path[-1] == '"':
        return path[1:-1]
    else:
        return path


def menu_set_out_dir():
    global output_path

    out_dir = console.input(Text("What is the output directory?\n", style=question_style))
    out_dir = menu_clean_path_string(out_dir)
    if menu_check_path_exist(out_dir):
        path = Path(out_dir)
        if not path.is_dir():
            console.print(f"Output path is a file not directory", style=style_warning, justify="left")
        output_path = out_dir


def generate_excel():
    global imx_file_path_1, imx_situation_1, imx_file_path_2, imx_situation_2

    imx = Imx(imx_file_path_1)

    if imx_file_path_1 == imx_file_path_2:
        imx_old = imx
    else:
        imx_old = Imx(imx_file_path_2)

    imx_situation_1 = imx.get_situation_repository(ImxSituationsEnum[imx_situation_1])
    imx_situation_2 = imx_old.get_situation_repository(ImxSituationsEnum[imx_situation_2])
    diff = ImxDiff(imx_situation_1, imx_situation_2)
    # todo: change name
    diff.generate_excel(f"{output_path}/diff.xlsx")


def open_excel_file(mapping_excel_path):
    file_path = Path(mapping_excel_path)
    console.print(file_path, justify="left")

    if platform.system() == "Darwin":  # macOS
        subprocess.call(("open", file_path))
    elif platform.system() == "Windows":  # Windows
        os.startfile(file_path)
    else:  # linux variants
        subprocess.call(("xdg-open", file_path))


def menu_view_log():
    with open(os.path.join("log.log"), "r") as f:
        print(f.read())
    console.input(Text("Hit key to continue...", style=info_style))


def excel_menu():
    menu_formatter = MenuFormatBuilder(max_dimension=Dimension(width=120, height=60))

    # noinspection PyTypeChecker
    menu = ConsoleMenu(root_menu_title, root_menu_subtitle, formatter=menu_formatter)

    menu.prologue_text = menu_prologue_text
    menu.epilogue_text = "Copyright (c) 2023-2033 ProRail - IDE"

    menu_imx_file_1 = FunctionItem("Set IMX file path 1", menu_set_imx_file_1, [])
    menu_imx_situation_1 = FunctionItem("Set situation for file 1", menu_set_imx_1_situation, [])
    menu_imx_file_2 = FunctionItem("Set IMX file path 2", menu_set_imx_file_2, [])
    menu_imx_situation_2 = FunctionItem("Set situation for file 2", menu_set_imx_2_situation, [])
    out_path = FunctionItem("Set output path", menu_set_out_dir, [])

    excel_generation = FunctionItem("Generate diff excel", generate_excel, [])
    open_excel = FunctionItem("Open Excel file", open_excel_file, ["diff.xlsx"])

    view_log = FunctionItem("View log", menu_view_log, [])
    save_settings = FunctionItem("Save settings", menu_save_settings, [])

    menu.append_item(menu_imx_file_1)
    menu.append_item(menu_imx_situation_1)
    menu.append_item(menu_imx_file_2)
    menu.append_item(menu_imx_situation_2)
    menu.append_item(out_path)
    menu.append_item(excel_generation)
    menu.append_item(open_excel)
    menu.append_item(view_log)
    menu.append_item(save_settings)

    about = SubmenuItem("About/help", get_about_menu(menu_formatter), menu=menu)
    menu.append_item(about)
    menu.show()


if __name__ == "__main__":
    excel_menu()
