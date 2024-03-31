 #!/usr/bin/env bash

# Generate extension list `code --list-extensions > vscode-extensions.txt`
cat vscode-extensions.txt | while read extension || [[ -n $extension ]];
do
  if code-server --install-extension $extension --force; then
    echo "Installed: $extension"
  else
    echo "Failed to install: $extension"
  fi
done
