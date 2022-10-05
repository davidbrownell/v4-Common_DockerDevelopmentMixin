# ----------------------------------------------------------------------
# |
# |  DockerDev.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-09-08 10:58:28
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
"""Functionality helpful when creating docker images."""

import shutil

from pathlib import Path
from typing import List, Optional

import typer

from typer.core import TyperGroup

from Common_Foundation.ContextlibEx import ExitStack
from Common_Foundation import PathEx
from Common_Foundation.Shell.All import CurrentShell
from Common_Foundation.SourceControlManagers.SourceControlManager import DistributedRepository, Repository, SourceControlManager
from Common_Foundation.SourceControlManagers.All import ALL_SCMS
from Common_Foundation.Streams.DoneManager import DoneManager, DoneManagerFlags
from Common_Foundation import SubprocessEx

from Common_FoundationEx.InflectEx import inflect


# ----------------------------------------------------------------------
class NaturalOrderGrouper(TyperGroup):
    # ----------------------------------------------------------------------
    def list_commands(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.commands.keys()


# ----------------------------------------------------------------------
app                                         = typer.Typer(
    cls=NaturalOrderGrouper,
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)


# ----------------------------------------------------------------------
@app.callback()
def PlaceholderFunc():
    """This function exists to ensure that there is more than one export defined in this file, thereby requiring the name of the method to invoke as the first parameter"""
    pass


# ----------------------------------------------------------------------
@app.command("BundleRepo", no_args_is_help=True)
def BundleRepo(
    repo_root: Path=typer.Argument(..., exists=True, file_okay=False, resolve_path=True, help="The root of the repository that you want to bundle."),
    bundle_filename: Path=typer.Argument(..., dir_okay=False, resolve_path=True, help="The name of the filename that you want to create."),
    working_dir: Path=typer.Argument(CurrentShell.CreateTempDirectory(create_dir=False), file_okay=False, resolve_path=True, help="The working dir used to process files and changes."),
    include_working_changes: bool=typer.Option(False, "--include-working-changes", help="Include working changes when bundling the repository."),
    preserve_working_dir: bool=typer.Option(False, "--preserve-working-dir", help="Do not delete the working directory upon program exit."),
    verbose: bool=typer.Option(False, "--verbose", help="Write verbose information to the terminal."),
    debug: bool=typer.Option(False, "--debug", help="Write additional debug information to the terminal."),
) -> None:
    """Bundles the contents of a repository for inclusion within a docker image."""

    if bundle_filename.suffix != ".tgz":
        bundle_filename = bundle_filename.parent / "{}.tgz".format(bundle_filename.name)

    with DoneManager.CreateCommandLine(
        output_flags=DoneManagerFlags.Create(verbose=verbose, debug=debug),
    ) as dm:
        scm: Optional[SourceControlManager] = None

        with dm.Nested(
            "Detecting SCM...",
            lambda: "none detected" if scm is None else scm.name,
        ) as scm_dm:
            for potential_scm in ALL_SCMS:
                if potential_scm.IsRoot(repo_root):
                    scm = potential_scm
                    break

            if scm is None:
                scm_dm.WriteError("No SCM was detected for use in '{}'.\n".format(repo_root))
                scm_dm.ExitOnError()

        assert scm is not None

        # Get the repository code
        source_repository = scm.Open(repo_root)
        dest_repository: Optional[Repository] = None

        if working_dir.is_dir() and any(True for item in working_dir.iterdir()):
            with dm.Nested(
                "Updating '{}'...".format(working_dir),
                suffix="\n",
            ) as update_dm:
                dest_repository = scm.Open(working_dir)

                if isinstance(dest_repository, DistributedRepository):
                    result = dest_repository.PullAndUpdate()
                else:
                    result = dest_repository.Update(None)

                update_dm.result = result.returncode

                if update_dm.result != 0:
                    update_dm.WriteError(result.output)
                    update_dm.ExitOnError()

                with update_dm.YieldVerboseStream() as stream:
                    stream.write(result.output)
        else:
            with dm.Nested(
                "Cloning into '{}'...".format(working_dir),
                suffix="\n",
            ):
                dest_repository = scm.Clone(str(repo_root), working_dir)

        assert dest_repository is not None

        if preserve_working_dir:
            # ----------------------------------------------------------------------
            def KeepDir():
                dm.WriteInfo("\n'{}' was preserved.".format(working_dir))

            # ----------------------------------------------------------------------

            on_exit_func = KeepDir
        else:
            # ----------------------------------------------------------------------
            def RemoveDir():
                with dm.Nested("\nRemoving working directory..."):
                    PathEx.RemoveTree(working_dir)

            # ----------------------------------------------------------------------

            on_exit_func = RemoveDir

        with ExitStack(on_exit_func):
            if include_working_changes:
                filenames: List[Path] = []

                with dm.Nested(
                    "Detecting working changes in '{}'...".format(repo_root),
                    lambda: "{} found".format(inflect.no("changed file", len(filenames))),
                ):
                    filenames += [path for path in source_repository.EnumWorkingChanges() if path.is_file()]
                    filenames += [path for path in source_repository.EnumUntrackedWorkingChanges() if path.is_file()]

                if filenames:
                    with dm.Nested(
                        "Copying {}...".format(inflect.no("file", len(filenames)),
                        suffix="\n",
                    ),
                ):
                        for source_filename in filenames:
                            partial_path = PathEx.CreateRelativePath(repo_root, source_filename)
                            dest_filename = working_dir / partial_path

                            dest_filename.parent.mkdir(parents=True, exist_ok=True)
                            shutil.copy(source_filename, dest_filename)

            archive_name = "archive.tgz"

            with dm.Nested(
                "Bundling content...",
                suffix="\n" if dm.is_verbose else None,
            ) as bundle_dm:
                command_line = 'tar -cz -f {} {} *'.format(
                    archive_name,
                    " ".join("--exclude {}".format(scm_working_dir) for scm_working_dir in (scm.working_directories or [])),
                )

                bundle_dm.WriteVerbose("Command line: {}".format(command_line))

                result = SubprocessEx.Run(
                    command_line,
                    cwd=working_dir,
                )

                bundle_dm.result = result.returncode

                if bundle_dm.result != 0:
                    bundle_dm.WriteError(result.output)
                    bundle_dm.ExitOnError()

                with bundle_dm.YieldVerboseStream() as stream:
                    stream.write(result.output)

            with dm.Nested(
                "Copying archive...",
            ):
                bundle_filename.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(working_dir / archive_name, bundle_filename)


# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
# ----------------------------------------------------------------------
if __name__ == "__main__":
    app()
