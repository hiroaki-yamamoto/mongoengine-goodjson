#!/bin/sh
# -*- coding: utf-8 -*-

${HOME}/.poetry/bin/poetry install
exec ${HOME}/.poetry/bin/poetry run tox -p all
