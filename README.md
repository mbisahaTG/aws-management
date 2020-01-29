# AWS Management
Wrappers around common AWS tasks.

## Installation
Install using pip

```bash
$ pip install git+https://github.com/stoolan/aws-management.git
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
# DB Instance config. See https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/rds.html#RDS.Client.create_db_instance for optional args
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

## Contributing
Contribution directions go here.

## License
The gem is available as open source under the terms of the [MIT License](https://opensource.org/licenses/MIT).
