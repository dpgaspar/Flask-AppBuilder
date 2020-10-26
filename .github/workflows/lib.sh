#!/bin/bash


setup-requirements()
{
  sudo apt-get update
  sudo apt-get install -y python-dev libldap2-dev libsasl2-dev libssl-dev
  pip install --upgrade pip
  pip install -r requirements.txt
  pip install -r requirements-dev.txt
  pip install -r requirements-extra.txt
}
