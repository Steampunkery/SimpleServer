import json
import sys
import time
import logging

from datetime import datetime

from argon2.exceptions import VerifyMismatchError
from argon2 import PasswordHasher

import web

logger = logging.getLogger(__name__)
logging.basicConfig()
logger.setLevel(logging.INFO)


class CookieUtils:
    @staticmethod
    def cookie_write_timer():
        """Call store_cookies once per hour"""
        while True:
            time.sleep(3600)  # An hour
            CookieUtils.store_cookies()
            logger.info("Storing cookies...")

    @staticmethod
    def cookie_check_timer():
        """Delete cookies that have expired, checking once per day"""
        while True:
            try:
                with open("cookies.json", "r+") as cookies_json:
                    cookies = json.load(cookies_json)
                    now = datetime.fromtimestamp(int(time.time()))
                    for cookie, timestamp in cookies.items():
                        if (now - datetime.fromtimestamp(timestamp)).days >= 30:
                            del cookies[cookie]
                    cookies_json.seek(0)
                    cookies_json.write(json.dumps(cookies))
                    cookies_json.truncate()
                    web.servers.COOKIES = cookies
            except IOError:
                logger.error("There was an error deleting cookies. It's probably safe to ignore this.")
            time.sleep(86404)  # A day plus some to avoid a collision with cookie_write_timer

    @staticmethod
    def store_cookies():
        """Write cookies from web.servers.COOKIES to cookies.json"""
        with open("cookies.json", "w") as cookies_json:
            json.dump(web.servers.COOKIES, cookies_json)


    @staticmethod
    def load_cookies() -> dict:
        """Return cookies loaded from cookies.json"""
        try:
            logger.info("Reading cookies...")
            with open("cookies.json", "r") as cookies_json:
                cookies = json.load(cookies_json)
            return cookies
        except IOError:
            logger.error("File cookies.json could not be opened for reading, please check file and restart server.")
            sys.exit(1)


class PasswordUtils:
    ph = PasswordHasher()

    @staticmethod
    def verify_password(username_attempt, password_attempt) -> bool:
        """Return a boolean indicating whether password verification succeeded"""
        try:
            PasswordUtils.ph.verify(web.servers.ACCOUNTS[username_attempt], password_attempt)
            logger.info(f"Successful login to account {username_attempt}")
            return True
        except (VerifyMismatchError, KeyError):
            logger.info(f"Failed login to account {username_attempt}")
            return False

    @staticmethod
    def store_passwords():
        """Write passwords from web.servers.ACCOUNTS to passwd"""
        with open("passwd", "w") as passwd_json:
            json.dump(web.servers.ACCOUNTS, passwd_json)


    @staticmethod
    def load_passwords() -> dict:
        """Return passwords loaded from passwd"""
        try:
            logger.info("Reading passwords...")
            with open("passwd", "r") as passwd_json:
                passwords = json.load(passwd_json)
            return passwords
        except IOError:
            logger.error("File passwd could not be opened for reading, please check file and restart server.")
            sys.exit(1)
