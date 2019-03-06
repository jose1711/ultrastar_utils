#!/bin/bash
# transpose song in Ultrastart TXT format
# usage:
#   transpose.sh SONG.TXT [-]SEMITONES
#
# example:
# transpose.sh SONG.TXT -13
#   transposes song one octave down

awk -F'[ ]' -v shift="$2" '!/^[:*]/{print; next} /^[:*]/{$4=$4+shift; print}' "$1"
