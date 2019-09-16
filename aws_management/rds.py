import boto3, botocore
from os import environ
from dotmap import DotMap
import logging
import jsonschema


class AwsRdsProvisionError(Exception):
    pass


class AwsRdsManager:
    log = logging.getLogger(__name__)
    db_schema = dict(
        type="object",
        properties=dict(
            database=dict(type="string"),
            password=dict(type="string"),
            username=dict(type="string"),
        ),
        required=["database", "password", "username"],
    )
    config_schema = dict(
        type="object",
        properties=dict(
            AllocatedStorage=dict(type="integer"),
            DBInstanceClass=dict(type="string"),
            Engine=dict(type="string"),
            BackupRetentionPeriod=dict(type="integer"),
            MultiAZ=dict(type="boolean"),
            EngineVersion=dict(type="string"),
            PubliclyAccessible=dict(type="boolean"),
            VpcSecurityGroupIds=dict(type="array", items=dict(type="string")),
            DBSubnetGroupName=dict(type="string"),
        ),
        required=[
            "AllocatedStorage",
            "DBInstanceClass",
            "Engine",
            "BackupRetentionPeriod",
            "MultiAZ",
            "EngineVersion",
            "PubliclyAccessible",
            "VpcSecurityGroupIds",
            "DBSubnetGroupName",
        ],
    )

    @classmethod
    def set_config(cls, config: dict):
        jsonschema.validate(config, cls.config_schema)
        cls.RDS_CONFIG = config

    def __init__(self, db: dict):
        jsonschema.validate(db, self.db_schema)
        self.db = db

    @property
    def boto_client(self):
        return boto3.client("rds")

    def database_description(self):
        rds = self.boto_client
        try:
            instances = rds.describe_db_instances(
                DBInstanceIdentifier=self.db["database"]
            )
            return DotMap(instances["DBInstances"][0])
        except (rds.exceptions.DBInstanceNotFoundFault, KeyError, IndexError) as ex:
            raise AwsRdsProvisionError(f"No Database Provisioned for {self.db}")

    def provision(self, silent=True, wait=False):
        assert hasattr(
            self.__class__, "RDS_CONFIG"
        ), f"No RDS Configuration Given. See {self.__class__.__name__}.set_config"
        db_vars = self.RDS_CONFIG.copy()
        db_vars.update(
            {
                "DBName": self.db["database"],
                "DBInstanceIdentifier": self.db["database"],
                "MasterUsername": self.db["username"],
                "MasterUserPassword": self.db["password"],
            }
        )
        try:
            self.boto_client.create_db_instance(**db_vars)
        except botocore.exceptions.ClientError as ex:
            if silent and "DBInstanceAlreadyExists" in ex.__str__():
                self.log.info(f"{self.db} instance already exists. Skipping.")
                return
            else:
                raise ex
        if wait:
            self.log.info(f"Waiting for {self.db} instance to spawn...")
            waiter = self.boto_client.get_waiter("db_instance_available")
            waiter.wait(DBInstanceIdentifier=db_vars["DBInstanceIdentifier"])
            self.log.info(f"{self.db} instance available.")
        else:
            self.log.warn(
                f"Warning: did not wait for {self.db} instance to spawn. Instance may not be available."
            )

    def deprovision(self, wait=False, silent=True):
        try:
            self.boto_client.delete_db_instance(
                DBInstanceIdentifier=self.db["database"],
                SkipFinalSnapshot=True,
                DeleteAutomatedBackups=True,
            )
        except botocore.exceptions.ClientError as ex:
            if silent and "DBInstanceNotFound" in ex.__str__():
                self.log.info(f"{self.db} instance already terminated. Skipping.")
                return
            else:
                raise ex
        if wait:
            self.log.info(f"Waiting for {self.db} instance to terminate...")
            waiter = self.boto_client.get_waiter("db_instance_deleted")
            waiter.wait(DBInstanceIdentifier=self.db["database"])
            self.log.info(f"{self.db} instance terminated.")
        else:
            self.log.warn(f"Warning: did not wait for {self.db} instance to terminate.")
