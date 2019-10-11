import boto3
import logging


class AwsS3Manager:
    log = logging.getLogger(__name__)

    @property
    def boto_client(self):
        return boto3.client("s3")

    def create_bucket(self, bucket_name, acl="private"):
        assert acl in [
            "private",
            "public-read",
            "public-read-write",
            "authenticated-read",
        ]
        # Create bucket
        self.boto_client.create_bucket(Bucket=bucket_name, ACL=acl)
        if acl == "private":
            self.boto_client.put_public_access_block(
                Bucket=bucket_name,
                PublicAccessBlockConfiguration={
                    "BlockPublicAcls": True,
                    "BlockPublicPolicy": True,
                    "IgnorePublicAcls": True,
                    "RestrictPublicBuckets": True,
                },
            )

    def delete_bucket(self, bucket_name):
        self.boto_client.delete_bucket(Bucket=bucket_name)

    def list_buckets(self):
        return self.boto_client.list_buckets()

    def upload_file(self, bucket_name, source_file_name, destination_file_name=None):
        if destination_file_name is None:
            destination_file_name = source_file_name
        response = self.boto_client.upload_file(
            source_file_name, bucket_name, destination_file_name
        )
        return response

    def download_file(self, bucket_name, source_file_name, destination_file_name):
        return self.boto_client.download_file(
            bucket_name, source_file_name, destination_file_name
        )

    def delete_file(self, bucket_name, object_name):
        self.boto_client.delete_object(Bucket=bucket_name, Key=object_name)

    def presigned_url(self, bucket_name, object_name, expiration=3600):
        response = self.boto_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
        return response
