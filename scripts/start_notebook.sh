#!/bin/bash
set -e
set -x
jupyter notebook --ip='*' --no-browser --allow-root
