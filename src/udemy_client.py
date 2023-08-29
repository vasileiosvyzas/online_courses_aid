import os
from datetime import datetime
from typing import Dict, List

import backoff
import requests
from dotenv import find_dotenv, load_dotenv
from requests.auth import HTTPBasicAuth
from requests.sessions import Session


class UdemyClient:
    """
    Class that contains functions for requesting and accessing the data from the Udemy API
    https://www.udemy.com/developers/affiliate/
    """

    def __init__(self) -> None:
        # find .env automagically by walking up directories until it's found
        dotenv_path = find_dotenv()

        # load up the entries as environment variables
        load_dotenv(dotenv_path)

        self.CLIENT_ID = os.environ.get("UDEMY_CLIENT_ID")
        self.CLIENT_SECRET = os.environ.get("UDEMY_CLIENT_SECRET")

    @backoff.on_exception(
        backoff.expo,
        (
            requests.exceptions.Timeout,
            requests.exceptions.RequestException,
            requests.exceptions.HTTPError,
        ),
        max_tries=8,
    )
    @backoff.on_predicate(backoff.constant, interval=60, jitter=None)
    def request_data(self, url: str, current_session: Session) -> Dict:
        """Simple function that makes a get request from a url provided and returns the response

        Args:
            url (str): the endpoint we want to access
            current_session (Session): establishing a session so that to use the same TCP connection

        Returns:
            response: the response payload for the request
        """
        headers = {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        }

        try:
            print(f"Making a request at: {datetime.now().strftime('%H:%M:%S:%f')}", flush=True)

            response = requests.get(
                url=url,
                auth=HTTPBasicAuth(self.CLIENT_ID, self.CLIENT_SECRET),
                timeout=30,
                headers=headers,
            )
            response.raise_for_status()

            print(response.headers)

            return response.json()

        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
            print(response.request.headers)
            print(response)
            raise
        except requests.exceptions.ConnectionError as errc:
            print("A network connection error occurred:", str(errc))
            raise SystemExit(errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
            raise
        except requests.exceptions.RequestException as err:
            print("OOps: Something Else", err)
            raise

    def has_next_page(self, response: Dict) -> bool:
        """Simple utility function to check the response for a next page url

        Args:
            response (Dict): the response payload from the request

        Returns:
            bool: True if there is a next page and False if there is not
        """

        if response["next"] is not None:
            return True
        else:
            return False

    def get_courses_list(self) -> List:
        """
        This function requests data from the course-list endpoint and gets all the results for each particular page
        then it requests the data for the next page and saves all the results in a list

        Returns:
            List: Big list of results with all the courses

        TODO: implement rate limitting and retry in case of failures
        TODO: decide on an appropriate page size
        """

        courses_list_endpoint = "https://www.udemy.com/api-2.0/courses/"
        session = requests.Session()

        print("Calling the API for the list of courses")

        # get the list of courses available on Udemy
        response = self.request_data(url=courses_list_endpoint, current_session=session)
        courses_list = response["results"]
        print(response)

        while self.has_next_page(response=response):
            print(f"Getting the next page {response['next']}")
            response = self.request_data(url=response["next"], current_session=session)
            courses_list.extend(response["results"])

        print("*** Got all the courses ***")
        return courses_list

    def get_course_details(self, course_id: str) -> Dict:
        """
        This function is responsible for requesting the details for a specific course from the API

        Args:
            course_id (str): the course we want the course details for

        Returns:
            Dict: A dictionary with the course details
        """

        # session = requests.Session()
        course_details_endpoint = f"https://www.udemy.com/api-2.0/courses/{course_id}/?fields[course]=title,headline,description,url,visible_instructors,primary_category,primary_subcategory,status_label"

        print(f"Making a call for course ID: {course_id}")

        single_courses_details = self.request_data(
            url=course_details_endpoint, current_session=None
        )

        print(f"Returning the details for course {course_id}")

        return single_courses_details

    def get_course_curriculum(self, course_id: str) -> List:
        """Gets a course id and returns the curriculum for this course by going through
        every page and storing the results in a list

        Args:
            course_id (str): the course we want the curriculum details for

        Returns:
            List: a list with all the results from all the pages for this specific course
        """

        session = requests.Session()
        course_curriculum_endpoint = f"https://www.udemy.com/api-2.0/courses/{course_id}/public-curriculum-items/?page_size=16"

        print(f"Calling the API for the curriculum of {course_id}")
        response = self.request_data(url=course_curriculum_endpoint, current_session=session)
        courses_curriculum = response["results"]

        while self.has_next_page(response=response):
            print(f"Getting the next page {response['next']}")
            next_page = response["next"]
            response = self.request_data(url=next_page, current_session=session)
            courses_curriculum.extend(response["results"])

        print(f"Returning the entire curriculum for course {course_id}")
        return courses_curriculum
