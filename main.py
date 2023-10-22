from json import dumps, loads
from sys import argv

FILE_LOCALS = locals()

def extract_color_names() -> None:
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


def main() -> None:
    pass

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
