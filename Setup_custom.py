# ----------------------------------------------------------------------
# |
# |  Setup_custom.py
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-09-07 09:56:39
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
# pylint: disable=missing-module-docstring

import os
import uuid

from pathlib import Path
from typing import Dict, List, Optional, Union

from Common_Foundation.Shell import Commands                                # type: ignore  # pylint: disable=import-error,unused-import
from Common_Foundation.Streams.DoneManager import DoneManager               # type: ignore  # pylint: disable=import-error,unused-import
from Common_Foundation import Types                                         # type: ignore  # pylint: disable=import-error,unused-import

from RepositoryBootstrap import Configuration                               # type: ignore  # pylint: disable=import-error,unused-import
from RepositoryBootstrap import Constants                                   # type: ignore  # pylint: disable=import-error,unused-import


@Configuration.MixinRepository
def GetConfigurations() -> Union[
    Configuration.Configuration,
    Dict[
        str,                                # configuration name
        Configuration.Configuration,
    ],
]:
    """Return configuration information for the repository"""

    return Configuration.Configuration(
        "",
        [
            Configuration.Dependency(
                uuid.UUID("DD6FCD30-B043-4058-B0D5-A6C8BC0374F4"),
                "Common_Foundation",
                "python310",
                "https://github.com/davidbrownell/v4-Common_Foundation.git",
            ),
        ],
        Configuration.VersionSpecs(
            [],                             # tools
            {},                             # libraries
        ),
    )


# ----------------------------------------------------------------------
def GetCustomActions(
    # Note that it is safe to remove any parameters that are not used
    dm: DoneManager,                                    # pylint: disable=unused-argument
    explicit_configurations: Optional[List[str]],       # pylint: disable=unused-argument
) -> List[Commands.Command]:
    """Return custom actions invoked as part of the setup process for this repository"""

    commands: List[Commands.Command] = []

    root_dir = Path(__file__).parent
    assert root_dir.is_dir(), root_dir

    # Create a link to the foundation's .pylintrc file
    foundation_root_file = Path(Types.EnsureValid(os.getenv(Constants.DE_FOUNDATION_ROOT_NAME))) / ".pylintrc"
    assert foundation_root_file.is_file(), foundation_root_file

    commands.append(
        Commands.SymbolicLink(
            root_dir / foundation_root_file.name,
            foundation_root_file,
            remove_existing=True,
            relative_path=True,
        ),
    )

    return commands
