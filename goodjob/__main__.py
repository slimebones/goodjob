import asyncio
import subprocess
import argparse
from pykit.err import ValueErr
from pykit.log import log
import sys
from pathlib import Path
from loguru import logger

GIT_FILES_CMD = "git ls-files --other --modified --exclude-standard"
GIT_COMMIT_CMD = "git add . && git commit -m \"{0}\""
GIT_TITLE_CORE = "update {0}"
GIT_TITLE_EXTRA_LIMIT = 50
VAR_DIR = Path(Path.home(), ".goodjob")
LOG_PATH = Path(VAR_DIR, "log/main.log")

def _cfg_logging():
    logger.remove(0)
    logger.add(
        sys.stderr,
        format="<green>{time}</green> | <level>{level}</level> - {message}",
        colorize=True,
        level="INFO")
    logger.add(
        LOG_PATH,
        format="{message}",
        backtrace=True,
        diagnose=True,
        serialize=True,
        rotation="100MB",
        level="INFO")

def _run_main(is_dry: bool):
    p = subprocess.run(
        GIT_FILES_CMD, shell=True, text=True, stdout=subprocess.PIPE)
    if p.returncode > 0:
        log.err(
            f"git ls files process returned code {p.returncode},"
            f" err content is {p.stderr}")
        exit(p.returncode)
    stdout = p.stdout
    if stdout == "":
        log.err("nothing to commit, git ls files returned nothing")
        exit(1)

    raw_names = list(filter(
        lambda l: l and not l.isspace(), stdout.split("\n")))
    # collect filenames, put them up until limit is reached
    extra = ""
    names = [raw_name.split("/")[-1] for raw_name in raw_names]
    names_len = len(names)
    for i, name in enumerate(names):
        fname = name
        # not last name receive comma
        if i + 1 < names_len:
            fname += ", "
        if len(extra) + len(name) >= GIT_TITLE_EXTRA_LIMIT:
            extra += "..."
            break
        extra += fname

    core = GIT_TITLE_CORE.format(extra)

    if is_dry:
        log.info(f"will commit message: \"{core}\"")
        return
    
    p = subprocess.run(
        GIT_COMMIT_CMD.format(core),
        shell=True,
        text=True,
        stdout=subprocess.PIPE)
    if p.returncode > 0:
        log.err(
            f"failed to commit: git returned code {p.returncode},"
            f" err content is {p.stderr}")
        exit(p.returncode)
    log.info(f"commited {len(raw_names)} entries with message {core}")

async def async_main():
    VAR_DIR.mkdir(parents=True, exist_ok=True)
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    _cfg_logging()

    main_parser = argparse.ArgumentParser()
    main_parser.add_argument(
        "-d",
        dest="is_dry",
        help="make a dry run",
        action="store_true")
    mode_subparser = main_parser.add_subparsers(dest="mode")
    mode_subparser.add_parser("help")
    args = main_parser.parse_args()

    if args.is_dry:
        log.info("DRY RUN")

    if args.mode is None:
        _run_main(is_dry=args.is_dry)
    else:
        raise ValueErr(f"unrecognized mode {args.mode}")

def main():
    asyncio.run(async_main())

if __name__ == "__main__":
    main()
