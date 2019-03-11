#!/bin/bash

FLASK_DEBUG=True
FLASK_APP=__init__.py flask run --host 0.0.0.0 --with-threads
