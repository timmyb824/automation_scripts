import argparse
import os
import time
from urllib.parse import quote

from proxmoxer import ProxmoxAPI
from proxmoxer.core import ResourceException


def get_vmid_from_name(proxmox, node, name):
    for vm in proxmox.nodes(node).qemu.get():
        if vm["name"] == name:
            return vm["vmid"]
    raise Exception(f"Could not find a VM or template named {name}")


def create_proxmox_vm(
    host,
    user,
    password,
    node,
    template_name,
    newid,
    new_vm_name,
    memory,
    ip,
    gateway,
    ssh_key_file,
):
    try:
        proxmox = ProxmoxAPI(
            host, port=443, user=user, password=password, verify_ssl=True, timeout=15
        )
    except Exception as exception:
        return f"Failed to connect to Proxmox API: {str(exception)}"

    try:
        template_vmid = get_vmid_from_name(proxmox, node, template_name)

        # Create a clone of the VM
        proxmox.nodes(node).qemu(template_vmid).clone.post(
            newid=newid, name=new_vm_name, full=1
        )

        # Get the configuration of the VM
        config = proxmox.nodes(node).qemu(newid).config.get()

        # Read and URL encode the ssh public key
        with open(ssh_key_file, "r", encoding="utf-8") as f:
            ssh_public_key = f.read().strip()
        ssh_public_key_encoded = quote(ssh_public_key)

        # Update the configuration
        proxmox.nodes(node).qemu(newid).config.set(
            cores=2,
            sockets=1,
            cpu="host",
            memory=memory,
            net0="virtio,bridge=vmbr0",
            ipconfig0=f"ip={ip}/24,gw={gateway}",
            sshkeys=ssh_public_key_encoded,
            ostype="other",
            scsihw="virtio-scsi-pci",
            bootdisk="scsi0",
        )

        # Resize the disk - use + to increase by that amount
        # This can be problematic - comment out if failing
        # proxmox.nodes(node).qemu(newid).resize.put(disk="scsi0", size="16G")

        return f"VM {new_vm_name} created successfully."

    except ResourceException as exception:
        return f"Proxmox command failed: {str(exception)}"
    except Exception as exception:
        return f"Unexpected error: {str(exception)}"


def delete_proxmox_vm(
    host, user, password, node, vm_name, max_attempts=2, retry_delay=5
):
    try:
        proxmox = ProxmoxAPI(
            host, port=443, user=user, password=password, verify_ssl=True, timeout=15
        )
    except Exception as exception:
        return f"Failed to connect to Proxmox API: {str(exception)}"

    try:
        vmid = get_vmid_from_name(proxmox, node, vm_name)

        # Stop the VM
        proxmox.nodes(node).qemu(vmid).status.stop.post()

        # Delete the VM
        attempts = 0
        while attempts < max_attempts:
            try:
                proxmox.nodes(node).qemu(vmid).delete()
                return f"VM {vm_name} deleted successfully."
            except ResourceException as exception:
                # Retry on resource exception
                attempts += 1
                time.sleep(retry_delay)
                if attempts >= max_attempts:
                    return f"Proxmox command failed after {max_attempts} attempts: {str(exception)}"
            except Exception as exception:
                return f"Unexpected error: {str(exception)}"

    except ResourceException as exception:
        return f"Proxmox command failed: {str(exception)}"
    except Exception as exception:
        return f"Unexpected error: {str(exception)}"


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--type", choices=["create", "delete"], required=True)
    args = parser.parse_args()

    if args.type == "create":
        print("Creating VM...\n")
        host = os.getenv("PROXMOX_HOST")
        user = os.getenv("PROXMOX_USER")
        password = os.getenv("PROXMOX_PASSWORD")
        node = os.getenv("PROXMOX_NODE")
        template_name = os.getenv("PROXMOX_TEMPLATE_NAME")
        newid = os.getenv("PROXMOX_NEWID")
        new_vm_name = os.getenv("PROXMOX_NEW_VM_NAME")
        memory = os.getenv("PROXMOX_MEMORY")
        ip = os.getenv("PROXMOX_IP")
        gateway = os.getenv("PROXMOX_GATEWAY")
        ssh_key_file = os.getenv("PROXMOX_SSH_KEY_FILE")

        if None in [
            host,
            user,
            password,
            node,
            template_name,
            newid,
            new_vm_name,
            memory,
            ip,
            gateway,
            ssh_key_file,
        ]:
            print("One or more environment variables are not set.")
        else:
            print(
                create_proxmox_vm(
                    host,
                    user,
                    password,
                    node,
                    template_name,
                    newid,
                    new_vm_name,
                    memory,
                    ip,
                    gateway,
                    ssh_key_file,
                )
            )
    elif args.type == "delete":
        print("Deleting VM...\n")
        host = os.getenv("PROXMOX_HOST")
        user = os.getenv("PROXMOX_USER")
        password = os.getenv("PROXMOX_PASSWORD")
        node = os.getenv("PROXMOX_NODE")
        vm_name = os.getenv("PROXMOX_NEW_VM_NAME")

        if None in [host, user, password, node, vm_name]:
            print("One or more environment variables are not set.")
        else:
            print(
                delete_proxmox_vm(
                    host,
                    user,
                    password,
                    node,
                    vm_name,
                )
            )
