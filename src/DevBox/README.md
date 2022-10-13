# DevBox

Linux image with ssh functionality that can be used as a development box.

It would be great to use https://github.com/linuxserver/docker-openssh-server (as it is MUCH better than what is here), but Alpine isn't supported with [VS Code](https://code.visualstudio.com/docs/remote/linux#_remote-host-container-wsl-linux-prerequisites).


## Build the Image

`docker build --tag <image_name> .`

## Create SSH Keys

### SSH
1. `docker run -it --rm --entrypoint ./SshKeygen.sh <image_name>`
2. Save the private and public keys as `ssh_key` and `ssh_key.pub` in a directory on the host; this directory will be referred to as `<keys_directory>` in the instructions that follow.

### GPG
1. `docker run -it --rm --entrypoint ./GpgKeygen.sh <image_name>`
2. Save the private and public keys as `gpg_key` and `gpg_key.pub` in a directory on the host; this directory will be referred to as `<keys_directory>` in the instructions that follow.

## Run the Container

`docker run -it -p 127.0.0.1:22:22 -v "<keys_directory>:/local/keys" -e SSH_PUBLIC_KEY=/local/keys/ssh_key.pub -e GPG_PUBLIC_KEY=/local/keys/gpg_key.pub dev_box`
