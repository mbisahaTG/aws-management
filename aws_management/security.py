import boto3
from botocore.exceptions import ClientError
import logging

# permitted_ips = [environ[val] for val in environ["PERMITTED_IPS"].split(",")]
# server_ip = socket.gethostbyname("https://www." + environ["TABLEAU_SERVER_DOMAIN_NAME"])


class AwsSecurityManager:
    log = logging.getLogger(__name__)

    @property
    def client(self):
        ec2 = boto3.client("ec2")
        return ec2

    def security_group_description(self, security_group_id: str) -> dict:
        groups = self.client.describe_security_groups(GroupIds=[security_group_id])
        assert groups.get("SecurityGroups")
        return groups["SecurityGroups"][0]

    def ip_permissions(self, port, ip):
        return {
            "IpProtocol": "tcp",
            "FromPort": port,
            "ToPort": port,
            "IpRanges": [{"CidrIp": f"{ip}/32"}],
        }

    def group_permissions(self, port, group_id):
        return {
            "IpProtocol": "tcp",
            "FromPort": port,
            "ToPort": port,
            "UserIdGroupPairs": [{"GroupId": group_id}],
        }

    def revoke_ingress(self, security_group_id):
        ec2 = boto3.resource("ec2")
        security_group = ec2.SecurityGroup(security_group_id)
        assert security_group
        try:
            security_group.revoke_ingress(IpPermissions=security_group.ip_permissions)
        except ClientError:
            self.log.info("Security ingress rules already revoked")
            pass

    def set_ingress_rule(self, security_group_id, permissions):
        self.client.authorize_security_group_ingress(
            GroupId=security_group_id, IpPermissions=[permissions]
        )

    def set_ingress_rules(self, security_group_id, ports=[], ips=[], allowed_groups=[]):
        self.revoke_ingress(security_group_id)
        for port in ports:
            for ip in ips:
                self.set_ingress_rule(security_group_id, self.ip_permissions(port, ip))
            for group in allowed_groups:
                self.set_ingress_rule(
                    security_group_id, self.group_permissions(port, group)
                )
