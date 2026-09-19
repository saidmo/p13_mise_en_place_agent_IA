#!/bin/sh
set -eu

umask 077

mkdir -p /root/.ssh
chmod 700 /root/.ssh

cp /run/ssh-input/id_ed25519_ollama /root/.ssh/id_ed25519_ollama
cp /run/ssh-input/known_hosts /root/.ssh/known_hosts

chmod 600 /root/.ssh/id_ed25519_ollama
chmod 600 /root/.ssh/known_hosts

exec autossh -M 0 "$@"