import json
import sys

import boto3
from botocore.exceptions import ClientError

ec2 = boto3.resource("ec2")
ec2_client = boto3.client("ec2")


def create_ec2_instance(security_group_id):
    instances = ec2.create_instances(
        ImageId="ami-053b0d53c279acc90",
        MinCount=1,
        MaxCount=1,
        InstanceType="t2.micro",
        KeyName="awsCommon",
        SecurityGroupIds=[
            security_group_id,
        ],
    )

    print("New instance created:", instances[0].id)
    return instances[0].id


def create_security_group():
    vpcs_response = ec2_client.describe_vpcs()
    vpc_id = vpcs_response.get("Vpcs", [{}])[0].get("VpcId", "")

    response = ec2_client.create_security_group(
        GroupName="linode-replacement", Description="linode-replacement", VpcId=vpc_id
    )
    security_group_id = response["GroupId"]
    print(f"Security Group Created {security_group_id} in vpc {vpc_id}.")

    data = ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
            },
        ],
    )

    print(f"Ingress Successfully Set {data}")
    return security_group_id


def delete_ec2_instance(instance_id):
    instance = ec2.Instance(instance_id)
    response = instance.terminate()
    print("Instance deleted:", response)


def delete_security_group(security_group_id):
    try:
        response = ec2_client.delete_security_group(GroupId=security_group_id)
        print("Security Group Deleted:", response)
    except ClientError as exception:
        print("Error: ", exception)


if __name__ == "__main__":
    command = sys.argv[1].lower()
    if command == "create":
        security_group_id = create_security_group()
        instance_id = create_ec2_instance(security_group_id)
        with open("aws_resources.txt", "w", encoding="utf-8") as file:
            json.dump(
                {"InstanceID": instance_id, "SecurityGroupID": security_group_id}, file
            )
    elif command == "delete":
        with open("aws_resources.txt", "r", encoding="utf-8") as file:
            resources = json.load(file)
        delete_ec2_instance(resources["InstanceID"])
        delete_security_group(resources["SecurityGroupID"])
    else:
        print("Invalid command. Use either 'create' or 'delete'.")

# TODO: The instance deletes but the security group does not due to a DependencyViolation
# TODO: I should remove the aws_resources.txt file after the instance and security group are deleted
