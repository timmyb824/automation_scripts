# Set current time for logs
now=$(TZ=America/New_York date +"%T")
echo -e "\nScript start time: $now"
echo -e "--------------------------------------------\n"

# Set user directory
path=/home/tbryant

# Backup storage directory
backupfolder=$path/mysql_backup/backups

# Remote backup storage directory
remote_backupfolder=/mnt/bryantnas/mysql_backups

# MySQL user
user=$MYSQL_USER

# Number of days to store the backup
keep_day=3

sqlfile=$backupfolder/all-database-$(date +%d-%m-%Y_%H-%M-%S).sql
zipfile=$backupfolder/all-database-$(date +%d-%m-%Y_%H-%M-%S).zip

# Create a backup (removed `-p $password` and used .my.cnf instead)
mysqldump  --defaults-file=$path/.my.cnf -u $user --all-databases > $sqlfile

if [ $? == 0 ]; then
  echo -e 'Sql dump created'
  echo -e "--------------------------------------------\n"
else
  echo 'mysqldump return non-zero code'
  exit
fi

# Compress backup
echo -e 'Compressing Sql file'
echo -e "--------------------------------------------\n"
zip -q $zipfile $sqlfile

if [ $? == 0 ]; then
  echo -e  'The backup was successfully compressed'
  echo -e "--------------------------------------------\n"
else
  echo 'Error compressing backup'
  exit
fi

rm $sqlfile
echo -e "$(basename ${zipfile}) was created successfully"
echo -e "--------------------------------------------\n"

# Copy to remote backup location
cp $zipfile $remote_backupfolder

if [ $? == 0 ]; then
  echo -e "Backup file copied to remote location successfully"
  echo -e "--------------------------------------------\n"
else
  echo 'Error copying backup file to remote location'
  exit
fi

echo -e "############################################"
echo -e "############################################\n"

# Delete old backups
find $backupfolder -mtime +$keep_day -delete
find $remote_backupfolder -mtime +$keep_day -delete

curl -fsS -m 10 --retry 5 -o /dev/null $HEALTHCHECKS_URL_MYSQL
