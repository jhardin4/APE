import argparse
import logging
import os

os.environ['QT_API'] = 'pyqt5'  # noqa: E402 force PyQt5 for now

from GUI.main import MainGui

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="""
            APE Main GUI Application
            """
    )
    parser.add_argument(
        "-l",
        "--live",
        help="The live coding version of this application",
        action="store_true",
    )
    parser.add_argument(
        "-d", "--debug", help="Enable debug messages", action="store_true"
    )
    args = parser.parse_args()

    # enable application debug logging
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    MainGui.start(live=args.live)
