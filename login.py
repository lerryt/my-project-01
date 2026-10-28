"""Page object for a standard username-and-password login form."""
from getpass import getpass

from selenium import webdriver
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.options import Options


class LoginPage:
    """Encapsulate interactions with a login page for UI tests."""

    USERNAME = (By.NAME, "username")
    PASSWORD = (By.NAME, "password")
    SUBMIT = (By.CSS_SELECTOR, "button[type='submit'], input[type='submit']")

    def __init__(self, driver: WebDriver, timeout: float = 10) -> None:
        self.driver = driver
        self.wait = WebDriverWait(driver, timeout)

    def enter_username(self, username: str) -> None:
        field = self.wait.until(EC.visibility_of_element_located(self.USERNAME))
        field.clear()
        field.send_keys(username)

    def enter_password(self, password: str) -> None:
        field = self.wait.until(EC.visibility_of_element_located(self.PASSWORD))
        field.clear()
        field.send_keys(password)

    def submit(self) -> None:
        self.wait.until(EC.element_to_be_clickable(self.SUBMIT)).click()

    def login(self, username: str, password: str) -> None:
        """Fill in credentials and submit the login form."""
        self.enter_username(username)
        self.enter_password(password)
        self.submit()

def main() -> None:
    options = Options()
    driver = webdriver.Chrome(options=options)
    try:
        driver.get("http://mail.163.com")
        username = input("Username: ")
        password = getpass("Password: ")
        LoginPage(driver).login(username, password)
        input("Press Enter to close the browser...")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
