#!/bin/bash
# ----------------------------------------------------------------------
# |
# |  SshKeygen.sh
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-10-13 13:03:20
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
echo "Generating SSH keys..."
ssh-keygen -t rsa -b 4096 -f ~/.ssh/auto_generated -N "" > /dev/NULL

echo "Copy these private and public keys and save them on the host; they will be deleted from this container."
echo ""
echo ""

cat ~/.ssh/auto_generated
rm ~/.ssh/auto_generated

echo ""
echo ""

cat ~/.ssh/auto_generated.pub
rm ~/.ssh/auto_generated.pub
