#!/usr/bin/env bash
VERSION=3.4.1
THEMES=(
    cerulean
    cosmo
    cyborg
    darkly
    flatly
    journal
    lumen
    paper
    readable
    sandstone
    simplex
    slate
    spacelab
    superhero
    united
    yeti
)


for THEME in "${THEMES[@]}"; do
   echo updating $THEME
   wget https://stackpath.bootstrapcdn.com/bootswatch/${VERSION}/${THEME}/bootstrap.min.css
   mv bootstrap.min.css ${THEME}.css
done

