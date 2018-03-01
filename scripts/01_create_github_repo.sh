#!/bin/bash
curl -s https://api.github.com/repos/vit-tucek/uhw_modules | grep "Not Found" > /dev/null || { echo >&2 "The repository uhw_modules already exists in vit-tucek.  Aborting."; exit 1; }

echo "Trying to create a new repository on github.com."
echo "You will be asked for the GitHub password corresponding to the user vit-tucek"
echo "vit-tucek/uhw_modules"
echo "Calculates nilpotent cohomology of unitarizable highest weight modules using Enright formula."

curl -s -u 'vit-tucek' https://api.github.com/user/repos -d '{"name":"uhw_modules","description":"Calculates nilpotent cohomology of unitarizable highest weight modules using Enright formula."}' >> install.log

echo "Repository successfully created."
