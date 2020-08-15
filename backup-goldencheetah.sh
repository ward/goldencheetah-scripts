#!/bin/bash

GOLDENCHEETAH_LIBRARY="$HOME/.goldencheetah"
GOLDENCHEETAH_DOT_CONFIG="$HOME/.config/goldencheetah.org"
TODAY=$(date +"%Y%m%d")

if [ ! -d "$GOLDENCHEETAH_LIBRARY" ]; then
  echo "Could not find $GOLDENCHEETAH_LIBRARY."
  exit 1
fi
if [ ! -d "$GOLDENCHEETAH_DOT_CONFIG" ]; then
  echo "Could not find $GOLDENCHEETAH_DOT_CONFIG."
  exit 1
fi

(
  set -x
  tar -czf "goldencheetah-library.$TODAY.tar.gz" $GOLDENCHEETAH_LIBRARY
)
(
  set -x
  tar -czf "goldencheetah-dot-config.$TODAY.tar.gz" $GOLDENCHEETAH_DOT_CONFIG
)
