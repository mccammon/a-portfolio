import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes  # AWS api does not guess type - be explicit

s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))

portfolio_bucket = s3.Bucket('portfolio.otlets.com')
build_bucket = s3.Bucket('portfoliobuild.otlets.com')

# Download to memory
portfolio_zip = StringIO.StringIO()
build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

# Exact files
with zipfile.ZipFile(portfolio_zip) as myzip:
  for name in myzip.namelist():
    obj = myzip.open(name)
    # Upload each object to S3 bucket
    # note: uses file extention to guess type
    portfolio_bucket.upload_fileobj(obj, name,
        ExtraArgs={'ContentType': mimetypes.guess_type(name)[0]})
    # Update object permissions
    portfolio_bucket.Object(name).Acl().put(ACL='public-read')
