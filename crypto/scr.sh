#!/bin/bash
git add .
git commit -m 'commit'
git push heroku master
heroku logs --tail
