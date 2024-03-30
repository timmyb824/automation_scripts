#!/bin/bash

# Exit script when a command fails
set -e

###########################
####### LOAD CONFIG #######
###########################

while [ $# -gt 0 ]; do
        case $1 in
        -c)
                CONFIG_FILE_PATH="$2"
                shift 2
                ;;
        *)
                ${ECHO} "Unknown Option \"$1\"" 1>&2
                exit 2
                ;;
        esac
done

if [ -z $CONFIG_FILE_PATH ]; then
        SCRIPTPATH=$(cd ${0%/*} && pwd -P)
        CONFIG_FILE_PATH="${SCRIPTPATH}/mysql_backup.config"
fi

if [ ! -r ${CONFIG_FILE_PATH} ]; then
        echo "Could not load config file from ${CONFIG_FILE_PATH}" 1>&2
        exit 1
fi

source "${CONFIG_FILE_PATH}"

###########################
### Perform the Backup ####
###########################

# Function to perform the database backup
perform_backup() {
        local path="$1"
        local user="$2"
        local sqlfile="$3"
        local zipfile="$4"
        local remote_backupfolder="$5"
        local backupfolder="$6"
        local keep_day="$7"

        # Create a backup (using .my.cnf for credentials)
        mysqldump --defaults-file="$path/.my.cnf" -u "$user" --all-databases >"$sqlfile"
        echo 'Sql dump created'
        echo "--------------------------------------------"

        # Compress backup
        echo 'Compressing Sql file'
        echo "--------------------------------------------"
        zip -q "$zipfile" "$sqlfile"
        echo 'The backup was successfully compressed'
        echo "--------------------------------------------"

        # Remove the uncompressed sql file
        rm "$sqlfile"
        echo "$(basename "$zipfile") was created successfully"
        echo "--------------------------------------------"

        # Copy to remote backup location
        if cp "$zipfile" "$remote_backupfolder"; then
                echo "Backup copied to remote folder successfully"
        else
                echo "Failed to copy backup to remote folder"
        fi


        # Delete old backups from local backup folder
        if find "$backupfolder" -mtime +"$keep_day" -print -delete | grep -q '.*'; then
                echo "Old backups in local folder deleted successfully"
        else
                echo "No old backups to delete in local folder or an error occurred"
        fi

        # Delete old backups from remote backup folder
        if find "$remote_backupfolder" -mtime +"$keep_day" -print -delete | grep -q '.*'; then
                echo "Old backups in remote folder deleted successfully"
        else
                echo "No old backups to delete in remote folder or an error occurred"
        fi
}

# Function to log messages with timestamps
log() {
        echo "$(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to send a signal to Healthchecks.io
signal_healthchecks() {
        local status=$1
        curl -m 10 --retry 5 "${HEALTHCHECKS_URL}/${status}" >/dev/null 2>&1
}

# perform backup
if perform_backup "$USER_PATH" "$DB_USER" "$SQLFILE" "$ZIPFILE" "$REMOTE_BACKUPFOLDER" "$BACKUPFOLDER" "$KEEP_DAY"; then
        log "Backups completed successfully."
        signal_healthchecks 0
else
        log "Backups failed."
        signal_healthchecks 1
        exit 1
fi

echo "############################################"
echo "Backup process completed successfully!"
echo "############################################"
