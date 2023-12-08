import os

import paramiko


def check_file_exists_and_remove(
    remote_host, remote_user, remote_password, key_file, file_path
):
    ssh_client = paramiko.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(
        hostname=remote_host,
        username=remote_user,
        password=remote_password,
        key_filename=key_file,
    )

    # Check if file exists
    stdin, stdout, stderr = ssh_client.exec_command(f"ls {file_path}")
    if stdout.channel.recv_exit_status() == 0:
        print("file does exist and will be deleted")
        # If file exists, remove it
        ssh_client.exec_command(f"rm {file_path}")

    # Restart rsyslog service
    ssh_client.exec_command("systemctl restart rsyslog")

    ssh_client.close()


# Example usage
remote_host = os.environ.get("REMOTE_HOST")
remote_user = os.environ.get("SSH_USER")
remote_password = os.environ.get("SSH_KEY_PASSWORD")
key_file = os.environ.get("SSH_KEY")
check_file_exists_and_remove(
    remote_host, remote_user, remote_password, key_file, "~/deleteme.txt"
)
print("script over")
