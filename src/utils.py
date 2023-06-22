import requests
import os
import json

from typing import Dict, List
from requests.auth import HTTPBasicAuth
from datetime import datetime
from dotenv import load_dotenv, find_dotenv




def upload_courses_list_file_to_s3_bucket(file_location: str, filename: str) -> None:
    """
    It takes the filename of the json file with all the courses and it will upload it to
    the S3 bucket
    :param filename:
    :param file_location:
    :return:
    """
    try:
        print('uploading to s3')
        session = boto3.Session(profile_name='iamadmin-portofolio-general')
        s3_resource = session.resource('s3')
        s3_resource.Bucket('udemy-courses-store').upload_file(file_location, filename)
    except Exception as e:
        print(e)
        print('something went wrong')