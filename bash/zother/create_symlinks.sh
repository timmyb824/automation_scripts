#!/bin/bash

# -------------------------------------------------------------
# This script will clone the dotfiles repository and create
# symlinks for the files listed in the file symlinks.txt.
# The file symlinks.txt should be in the same directory as
# this script. The format of the file should be:
#  /path/to/original/file /path/to/symlink
# -------------------------------------------------------------

# Define the path to the file containing the symlink paths
FILE_WITH_PATHS="./symlinks.txt"

# Function to check if git is installed
check_git_installed() {
    if ! command -v git &> /dev/null; then
        echo "git could not be found. Please install git."
        exit 1
    fi
}

# Function to clone the repository
clone_repo() {
    local repo_url="https://github.com/timmyb824/dotfiles.git"
    local dest_dir="$HOME/.config/dotfiles"

    # Check if ~/.config exists, if not create it
    if [ ! -d "$HOME/.config" ]; then
        echo "Creating $HOME/.config directory..."
        mkdir -p "$HOME/.config"
    fi

    # Clone the dotfiles repository if it hasn't been cloned already
    if [ ! -d "$dest_dir" ]; then
        echo "Cloning the dotfiles repository..."
        git clone "$repo_url" "$dest_dir"
    else
        echo "The dotfiles repository already exists at $dest_dir."
    fi
}

# Check if git is installed
check_git_installed

# Clone the dotfiles repository
clone_repo

echo "Dotfiles installation process completed."
echo "Creating symlinks..."

# Check if the provided file exists
if [ ! -f "$FILE_WITH_PATHS" ]; then
    echo "The file $FILE_WITH_PATHS does not exist."
    exit 1
fi

# Loop through each line in the file
while IFS=' ' read -r original_path symlink_path; do
    # Expand tilde to $HOME
    original_path="${original_path/#\~/$HOME}"
    symlink_path="${symlink_path/#\~/$HOME}"

    # Check if the original file exists
    if [ ! -e "$original_path" ]; then
        echo "Warning: The original file $original_path does not exist. Skipping symlink creation."
        continue
    fi

    # Create the symlink, first making sure the directory for the symlink exists
    mkdir -p "$(dirname "$symlink_path")"
    ln -sfn "$original_path" "$symlink_path"
    echo "Symlink created for $original_path -> $symlink_path"
done < "$FILE_WITH_PATHS"

echo "Symlink creation process completed."
