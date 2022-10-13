# ----------------------------------------------------------------------
# |
# |  Dockerfile
# |
# |  David Brownell <db@DavidBrownell.com>
# |      2022-10-13 08:40:50
# |
# ----------------------------------------------------------------------
# |
# |  Copyright David Brownell 2022
# |  Distributed under the Boost Software License, Version 1.0. See
# |  accompanying file LICENSE_1_0.txt or copy at
# |  http://www.boost.org/LICENSE_1_0.txt.
# |
# ----------------------------------------------------------------------
FROM ubuntu:latest

RUN apt-get update

# Set the time zone
RUN DEBIAN_FRONTEND=noninteractive \
    && apt-get install -y tzdata \
    && rm /etc/localtime \
    && ln -sf /usr/share/zoneinfo/America/Los_Angeles /etc/localtime

# Install the dependencies
RUN apt-get install -y \
    git \
    gnupg \
    nano \
    openssh-server

# Clean
RUN rm -rf /var/lib/apt/lists/* /var/tmp/*

# Update ssh_config
RUN echo "PubkeyAuthentication yes" >> /etc/ssh/sshd_config \
    && echo "PasswordAuthentication no" >> /etc/ssh/sshd_config

# Prime gpg
RUN gpg --list-keys

COPY ImageContent /

ENTRYPOINT ["./EntryPoint.sh"]
