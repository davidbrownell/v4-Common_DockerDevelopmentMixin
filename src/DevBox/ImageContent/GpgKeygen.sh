#!/bin/bash
# ----------------------------------------------------------------------
# |
# |  GpgKeygen.sh
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-10-13 14:30:03
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
gpg --full-generate-key | tee gpg_output.log

# Get the key id
gpg_id=`egrep "^\s+([A-F0-9]+)$" gpg_output.log | xargs`
rm gpg_output.og

echo "Copy these private and public keys and save them on the host; they will be deleted from this container."
echo ""
echo ""

gpg --armor --export-secret-key ${gpg_id}
echo ""
echo ""

gpg --armor --export ${gpg_id}
echo ""
echo ""

gpg --batch --yes --delete-secret-keys ${gpg_id}
gpg --batch --yes --delete-keys ${gpg_id}
