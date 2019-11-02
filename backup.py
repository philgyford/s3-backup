#!/usr/bin/env python3
import argparse
from datetime import datetime, timedelta
import logging
import os
import time

from sultan.api import Sultan
import yaml


logging.basicConfig(level=logging.INFO, format="%(message)s")
LOGGER = logging.getLogger(__name__)

# Where expect to find the config file:
current_dir = os.path.realpath(os.path.dirname(__file__))
CONFIG_FILE = os.path.join(current_dir, "config.yaml")


class S3Backup:

    dryrun = False

    profiles = []

    def __init__(self, dryrun=False):
        """Set dryrun and load config.

        Keyword arguments:
        dryrun -- boolean, whether this is a dry-run or not.
        """
        self.dryrun = dryrun

        self._load_config(CONFIG_FILE)

    def _load_config(self, config_file):
        "Set object variables based on supplied config file."

        with open(config_file, "r") as stream:
            try:
                self.profiles = yaml.safe_load(stream)
            except yaml.YAMLError as err:
                LOGGER.critical("Error parsing config.yaml: {}".format(err))
                exit()

        if self.profiles is None:
            LOGGER.critical("No config found in the config file {}".format(config_file))
            exit()

    def run_backup(self):
        """Do the backup, for real or dry run."""

        if self.dryrun is False:
            LOGGER.info("\nNot a dry run: Eligible files will be downloaded\n")
        else:
            LOGGER.info("\nDRY RUN: Nothing will be downloaded\n")

        for profile, config in self.profiles.items():
            for paths in config["paths"]:

                # --no-progress : File transfer progress is not displayed.
                command = (
                    "s3 sync {remote} {local} --profile={profile} --no-progress"
                ).format(remote=paths["remote"], local=paths["local"], profile=profile)

                args = []

                if "delete" in paths and paths["delete"] is True:
                    # Delete local files that don't exist on S3:
                    args.append("--delete")

                if "include-only" in paths:
                    includes = []
                    if "today" in paths["include-only"]:
                        fmt = paths["include-only"]["today"]
                        dt = datetime.utcnow()
                        includes.append("--include '{}'".format(dt.strftime(fmt)))
                    if "yesterday" in paths["include-only"]:
                        fmt = paths["include-only"]["yesterday"]
                        dt = datetime.utcnow() - timedelta(1)
                        includes.append("--include '{}'".format(dt.strftime(fmt)))

                    if len(includes) > 0:
                        args.append(" --exclude '*'")
                        args.extend(includes)

                if self.dryrun is True:
                    # The aws command has its own dryrun option, handily:
                    args.append("--dryrun")

                command = "{} {}".format(command, " ".join(args))

                with Sultan.load() as s:
                    result = s.aws(command).run(streaming=True)
                    # From https://sultan.readthedocs.io/en/latest/sultan-examples.html#example-13-streaming-results-from-a-command  # noqa: E501
                    while True:
                        complete = result.is_complete
                        for line in result.stdout:
                            LOGGER.info(line)
                        for line in result.stderr:
                            LOGGER.error(line)
                        if complete:
                            break
                        time.sleep(1)


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Backup remote S3 buckets to local folders"
    )

    parser.add_argument(
        "--dryrun",
        default=False,
        action="store_true",
        help="Outputs the aws commands that would be run, but downloads nothing",
    )

    args = parser.parse_args()

    S3Backup(dryrun=args.dryrun).run_backup()

    exit(0)
