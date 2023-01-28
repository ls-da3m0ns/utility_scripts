from tempfile import mkdtemp
from selenium import webdriver
from selenium_stealth import stealth
from webdriver_manager.chrome import ChromeDriverManager
import logging

class silent_selenium():
    driver = None
    SELENIUM_TIMEOUT = 10
    def __init__(self , webdriver_path = None, binary_location = None ) -> None:
        if self.driver is None:
            self.driver = self.selenium_init(webdriver_path, binary_location)
        
    def selenium_init(self, webdriver_path = None, binary_location = None):
        options = webdriver.ChromeOptions()
        logging.info()("starting new selenium")
        if binary_location is not None: options.binary_location = binary_location
        options.add_argument("--window-size=1920,1080")
        options.add_argument("--start-maximized")
        options.add_argument("--headless")
        options.add_argument('--no-sandbox')
        options.add_argument("--disable-gpu")
        options.add_argument("--single-process")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-dev-tools")
        options.add_argument("--no-zygote")
        options.add_argument(f"--user-data-dir={mkdtemp()}")
        options.add_argument(f"--data-path={mkdtemp()}")
        options.add_argument(f"--disk-cache-dir={mkdtemp()}")
        options.add_argument("--remote-debugging-port=9222")


        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option('useAutomationExtension', False)
        if webdriver_path is not None: driver = webdriver.Chrome(webdriver_path, options=options)
        else: driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)

        stealth(driver,
            languages=["en-US", "en"],
            vendor="Google Inc.",
            platform="Win32",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
            )

        self.driver = driver
        return driver

    def restart_driver(self):
        self.driver.close()
        self.driver.quit()
        self.driver = self.selenium_init()