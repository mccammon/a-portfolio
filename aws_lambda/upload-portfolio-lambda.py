import boto3
from botocore.client import Config
import StringIO
import zipfile
import mimetypes  # AWS api does not guess type - be explicit

def lambda_handler(event, context):
    try:
        s3 = boto3.resource('s3', config=Config(signature_version='s3v4'))
        sns = boto3.resource('sns')
        topic = sns.Topic('arn:aws:sns:us-west-2:524410732490:deployPortfolioTopic')

        portfolio_bucket = s3.Bucket('portfolio.otlets.com')
        build_bucket = s3.Bucket('portfoliobuild.otlets.com')

        # Download to memory
        portfolio_zip = StringIO.StringIO()
        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        # Exact files
        with zipfile.ZipFile(portfolio_zip) as myzip:
          for name in myzip.namelist():
            obj = myzip.open(name)
            print(name)
            # Upload each object to S3 bucket
            # note: uses file extention to guess type
            portfolio_bucket.upload_fileobj(obj, name,
                ExtraArgs={'ContentType': mimetypes.guess_type(name)[0]})
            # Update object permissions
            portfolio_bucket.Object(name).Acl().put(ACL='public-read')

        topic.publish(Subject='Portfolio Deployment', Message='Portfolio deployed successfully!')
        return "Job Done!"
    except:
        topic.publish(Subject='Portfolio Deployment Failed', Message='Portfolio deoployment failed')
        raise
