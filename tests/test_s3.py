from aws_management.s3 import AwsS3Manager
import json
import pytest
import os


@pytest.fixture
def bucket():
    return "sams-supercool-bucket"


@pytest.fixture
def manager(bucket):
    m = AwsS3Manager()
    m.create_bucket(bucket, acl="private")
    yield m
    m.delete_bucket(bucket)


@pytest.fixture
def file():
    os.system("> foo.txt")
    yield "foo.txt"
    os.system("rm foo.txt")


def j(dat):
    print(json.dumps(dat, sort_keys=True, indent=4))


def test_upload(manager, file, bucket):
    manager.upload_file(bucket, file)
    url = manager.presigned_url(bucket, file)
    assert isinstance(url, str)
    assert url.startswith("https://")
    manager.delete_file(bucket, file)
