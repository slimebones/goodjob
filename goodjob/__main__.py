import asyncio
import argparse
from pykit.err import ValueErr

async def async_main():
    main_parser = argparse.ArgumentParser()
    mode_subparser = main_parser.add_subparsers(dest="mode")
    mode_subparser.add_parser("help")
    args = main_parser.parse_args()

    if args.mode is None:
        pass
    else:
        raise ValueErr(f"unrecognized mode {args.mode}")

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
