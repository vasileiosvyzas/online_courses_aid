import os
import time
from typing import Dict, List

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

    def request_data(self, url: str, current_session: Session) -> Dict:
        """Simple function that makes a get request from a url provided and returns the response

        Args:
            url (str): the endpoint we want to access
            current_session (Session): establishing a session so that to use the same TCP connection

        Returns:
            response: the response payload for the request
        """

        try:
            response = current_session.get(
                url=url, auth=HTTPBasicAuth(self.CLIENT_ID, self.CLIENT_SECRET), timeout=10
            )
            response.raise_for_status()

            return response.json()

        except requests.exceptions.HTTPError as errh:
            print(errh)
            raise
        except requests.exceptions.ConnectionError as errc:
            print(errc)
            raise
        except requests.exceptions.Timeout as errt:
            print(errt)
            raise
        except requests.exceptions.RequestException as err:
            print(err)
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
        session = requests.Session()

        courses_list_endpoint = "https://www.udemy.com/api-2.0/courses/?page_size=6"

        # get the list of courses available on Udemy
        response = self.request_data(url=courses_list_endpoint, current_session=session)
        courses_list = response["results"]
        print(response)

        while self.has_next_page(response=response):
            print(response["next"])
            time.sleep(10)
            response = self.request_data(url=response["next"], current_session=session)
            courses_list.extend(response["results"])

        return courses_list

    def get_course_details(self, course_id: str) -> Dict:
        """
        This function is responsible for requesting the details for a specific course from the API

        Args:
            course_id (str): the course we want the course details for

        Returns:
            Dict: A dictionary with the course details
        """

        session = requests.Session()
        course_details_endpoint = f"https://www.udemy.com/api-2.0/courses/{course_id}/?fields[course]=title,headline,description,url,visible_instructors,primary_category,primary_subcategory,status_label"

        single_courses_details = self.request_data(
            url=course_details_endpoint, current_session=session
        )
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
        course_curriculum_endpoint = f"https://www.udemy.com/api-2.0/courses/{course_id}/public-curriculum-items/?page_size=6"

        response = self.request_data(url=course_curriculum_endpoint, current_session=session)
        courses_curriculum = response["results"]

        while self.has_next_page(response=response):
            next_page = response["next"]
            time.sleep(2)
            response = self.request_data(url=next_page, current_session=session)
            courses_curriculum.extend(response["results"])

        return courses_curriculum
