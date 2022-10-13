#!/bin/bash
# ----------------------------------------------------------------------
# |
# |  EntryPoint.sh
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-10-13 11:07:44
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
# There is a lot that I don't like about this script (for example, I don't
# like how it is manually starting the ssh service and calling bash at the
# end), however, I wasn't able to get this functionality working when invoked
# within the dockerfile. Keep it here for now and make updates if it turns
# out to be a problem.
service ssh start

if [[ ! -e ~/.ssh/authorized_keys ]]; then
    echo "# ----------------------------------------------------------------------"
    echo "# |"
    echo "# |  Adding 'SSH_PUBLIC_KEY'"
    echo "# |"
    echo "# ----------------------------------------------------------------------"

    if [[ -z "${SSH_PUBLIC_KEY}" ]]; then
        echo "The environment variable 'SSH_PUBLIC_KEY' was not defined!"
        exit -1
    fi

    if [[ ! -e ~/.ssh ]]; then
        mkdir ~/.ssh
    fi

    touch ~/.ssh/authorized_keys
    chmod 700 ~/.ssh/authorized_keys

    cat ${SSH_PUBLIC_KEY} >> ~/.ssh/authorized_keys
fi

if [[ ! -z "${GPG_PRIVATE_KEY}" ]]; then
    if [[ -z `gpg --list-keys | xargs` ]]; then
        echo "# ----------------------------------------------------------------------"
        echo "# |"
        echo "# |  Adding 'GPG_PRIVATE_KEY'"
        echo "# |"
        echo "# ----------------------------------------------------------------------"
        gpg --import "${GPG_PRIVATE_KEY}"

        gpg_id=`gpg --list-secret-keys | egrep "^\s+([A-F0-9]+)$" | xargs`

        gpg --edit-key ${gpg_id} trust quit
        git config --global user.signingkey ${gpg_id}
    fi
fi

/bin/bash
