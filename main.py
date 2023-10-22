from json import dumps, loads
from os import scandir
from os.path import splitext
from sys import argv

FILE_LOCALS = locals()

THEME_NAME = "Hush"
THEME_FILE_EXTENSION = "-color-theme.json"

def extract_color_names() -> dict:
    config = None
    with open("./src/config.json") as file:
        config = loads(file.read())

    colors = []
    colors.extend(
        color
        for color in config.get("colors", {})
        if color not in colors
    )
    colors.extend(
        color
        for color in config.get("tokenColors", {})
        if color not in colors
    )
    with open("./colors.hidden.json", "w+") as file:
        file.write(dumps(colors))

    return colors


def test_colors_config(config: dict) -> None:
    scopes = []
    scopes_with_dupes = []

    for scopes in config.get("colors", {}).values():
        for scope in scopes:
            if scope not in scopes:
                scopes.append(scope)
                continue

            scopes_with_dupes.append(scope)

    if scopes_with_dupes:
        scope_with_dupes = "\n".join(scopes_with_dupes)
        error_message = f"Scopes:\n{scope_with_dupes}"
        raise AssertionError(error_message)


def test_token_colors_config(config: dict) -> None:
    scopes = []
    scopes_with_dupes = []

    for config_groups in config.get("tokenColors", {}).values():
        for config_group in config_groups:
            font_style = config_group.get("fontStyle", None)
            for scope in config_group.get("scopes", []):
                scope_setting = (scope, font_style)
                if scope_setting not in scopes:
                    scopes.append(scope_setting)
                    continue

                scopes_with_dupes.append(scope)

    if scopes_with_dupes:
        scope_with_dupes = "\n".join(scopes_with_dupes)
        error_message = f"Token scopes:\n{scope_with_dupes}"
        raise AssertionError(error_message)


def create_theme(
    colors: dict,
    config: dict,
    name: str,
) -> dict:
    theme = {}
    theme_colors = {}
    theme_token_colors = []

    for color_name, color_scopes in config.get("colors", {}).items():
        color = colors.get(color_name, None)
        if color is None:
            continue

        for color_scope in color_scopes:
            theme_colors[color_scope] = color

    for color_name, config_groups in config.get("tokenColors", {}).items():
        color = colors.get(color_name, None)

        if color is None:
            continue

        for config_group in config_groups:
            token_color = {}
            settings = {}
            config_group_scope = config_group.get("scope", [])
            config_group_scope.sort()
            token_color["scope"] = config_group_scope
            settings["foreground"] = color

            font_style = config_group.get("fontStyle", None)
            if font_style is not None:
                settings["fontStyle"] = font_style

            token_color["settings"] = settings
            theme_token_colors.append(token_color)

    theme["colors"] = dict(sorted(theme_colors.items()))
    theme["tokenColors"] = theme_token_colors

    with open(f"./themes/{name}{THEME_FILE_EXTENSION}", "w") as file:
        file.write(dumps(theme, indent=2))

    return theme


def create_theme_files() -> None:
    base = None
    with open("./src/base.json") as file:
        base = loads(file.read())

    config = None
    with open("./src/config.json") as file:
        config = loads(file.read())

    create_theme(
        colors=base,
        config=config,
        name=THEME_NAME,
    )

    with scandir("./src/themes") as directory_entries:
        for entry in directory_entries:
            if not entry.is_file():
                continue

            variant_theme = base.copy()
            with open(entry) as file:
                current_config = loads(file.read())
                for color_name, color_value in current_config.items():
                    variant_theme[color_name] = color_value

            create_theme(
                colors=variant_theme,
                config=config,
                name=f"{THEME_NAME} {splitext(entry.name)[0]}",
            )



def main() -> None:
    create_theme_files()


def _main() -> None:
    arguments = argv
    action = argv[1] if len(argv) >= 2 else None

    if action is None:
        main()
        return

    action = FILE_LOCALS.get(action, None)
    if (
        (action is None)
        or (not callable(action))
        or (action.__module__ != __name__)
    ):
        main()
        return

    action(*arguments[2:])

if __name__ == "__main__":
    _main()
