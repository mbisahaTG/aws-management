# AWS Management
Wrappers around common AWS tasks.

## Installation
Install using pip

```bash
$ pip install git+https://github.com/stoolan/aws-management.git
```

If you are using `requirements.txt`, install in editable mode:

```bash
$ pip install -e git+https://github.com/stoolan/aws-management.git#egg=aws_management
```

## Usage

### RDS Resources

Import:
```python
from aws_management.rds import AwsRdsManager
```

Use on Existing DB:

```python
db = dict(
  database = 'an-rds-db-instance-identifier',
  password = 'a-secure-password',
  username = 'a-username'
)
manager = AwsRdsManager(db)
desc = manager.database_description()
print(desc)
# {
#    'DBInstanceIdentifier': 'an-rds-db-instance-identifier',
#    'DBInstanceClass': 'db.t3.micro',
#    'Engine': 'postgres',
#    'DBInstanceStatus': 'available',
#    'Endpoint': {
#    'Address': 'somehwere.somehost.us-east-1.rds.amazonaws.com',
#     'Port': 5432,
#     ...},
# ...}
```

De-provision Existing DB:
```python
manager = AwsRdsManager(db)
manager.deprovision(
  wait = True, # do not exit function until deprovision is complete
  silent = True # do not raise error if db instance does not exist
)
```

Provision new DB:
```python
# DB Instance config.
# See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html#RDS.Client.create_db_instance
# for configuration options
new_db_config = {
 'AllocatedStorage': 20,
 'DBInstanceClass': 'db.t3.micro',
 'Engine': 'postgres',
 'BackupRetentionPeriod': 7,
 'MultiAZ': False,
 'EngineVersion': '11.4',
 'PubliclyAccessible': True,
 'VpcSecurityGroupIds': ['your-sg-identifier'],
 'DBSubnetGroupName': 'an-rds-subnet-name'
 }
AwsRdsManager.set_config(new_db_config)
manager = AwsRdsManager(db)
manager.provision(
  wait = "db_instance_available", # do not exit function before instance creation is complete
  silent = True # do not raise error if db instance already exists
)
```

### S3 Resources

Import:
```python
from aws_management.s3 import AwsS3Manager

s3_manager = AwsS3Manager()
```

Create Bucket
```python
s3_manager.create_bucket("test-bucket", acl="private")
```

Delete Bucket
```python
s3_manager.delete_bucket("test-bucket")
```

List Buckets
```python
s3_manager.list_buckets()
# {'ResponseMetadata': {... 'server': 'AmazonS3'}},
#  'Buckets': [
#    {
#     'Name': 'test-bucket',
#     'CreationDate': datetime.datetime(2017, 8, 9, 18, 23, 56, tzinfo=tzutc())
#    },
#    ...
#  ]
# }
```

Upload File
```python
s3_manager.upload_file("test-bucket", "test.txt", "destination-prefix/test.txt")
```

Upload File Stream
```python
s3_manager.upload_file_stream("test-bucket", open("test.txt"), "destination-prefix/test.txt")
```

Download File
```python
s3_manager.download_file(
  "test-bucket",
  "destination-prefix/test.txt",
  "/path/to/local/test.txt"
)
```
Delete File
```python
s3_manager.delete_file("test-bucket", "destination-prefix/test.txt")
```

Generate Presigned URL:
```python
url = s3_manager.presigned_url("test-bucket", "test.txt", expiration=3600)
print(url)
# https://test-bucket.s3.amazonaws.com/test.txt?AWSAccessKeyId=XXXXXXX&Signature=XXXXXXX&Expires=1580327011
```

### EC2 Security Ingress Rules

Import:
```python
from aws_management.security import AwsSecurityManager
security_manager = AwsSecurityManager()
```

Describe Existing security group:
```python
security_manager.security_group_description('sg-group-id')
# {'Description': 'Test security group',
#  'GroupName': 'sg-group-id',
#  'IpPermissions': [{'FromPort': 80,
#    'IpProtocol': 'tcp',
#    'IpRanges': [{'CidrIp': '0.0.0.0/0'}],
#    'Ipv6Ranges': [{'CidrIpv6': '::/0'}],
#    'PrefixListIds': [],
#    'ToPort': 80,
#    'UserIdGroupPairs': [{'GroupId': 'sg-XXXXXX',
#      'UserId': '342637690033'}]},
```

Revoke all ingress rules
```python
security_manager.revoke_ingress('sg-group-id')
```

Reset all ingress rules
```python
# Only allow "another-security-group" and an IP to access port 22
security_manager.set_ingress_rules(
  'sg-group-id',
  ports = [22],
  ips = ['XX.XXX.XXX.XX'],
  allowed_groups = ["another-security-group"]
)
```

Add incremental IP access:
```python
new_ip = 'XX.XXX.XXX.XX'
allowed_ports = [22, 443]

permissions = [security_manager.ip_permisions(port, new_ip) for port in allowed_ports]

security_manager.set_ingress_rule('sg-group-id', permissions)

```

Add incremental Security Group access:
```python
new_sg = "another-security-group"
allowed_ports = [22, 443]

permissions = [security_manager.group_permisions(port, new_sg) for port in allowed_ports]

security_manager.set_ingress_rule('sg-group-id', permissions)

```

## Contributing
Contribution directions go here.

## License
The gem is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).
