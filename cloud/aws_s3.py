import boto3 
def create_session(aws_key, aws_secret):
    session = boto3.Session(
        aws_access_key_id=aws_key,
        aws_secret_access_key=aws_secret,
    )
    return session

def create_client(session):
    return session.client('s3')

def list_directory(session, bucket, directory):
    s3 = session.resource('s3')
    bucket = s3.Bucket(bucket)
    all_files = []
    for obj in bucket.objects.filter(Prefix=directory):
        all_files.append(obj.key)
    return all_files

def copy_file(session, bucket, source, destination):
    s3 = session.resource('s3')
    s3.Object(bucket, destination).copy_from(CopySource=bucket + '/' + source)

def download_file(client, bucket, source, destination):
    client.download_file(bucket, source, destination)

def upload_folder(client, bucket, source, destination):
    ...

def download_folder(client, bucket, source, destination):
    ...

def sync_folder(client, bucket, source, destination):
    ...

