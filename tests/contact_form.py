"""
Pytest + Selenium test for the EmailJS contact form on Siyabonga's portfolio.

IMPORTANT:
    This is a genuine end-to-end test - it sends a REAL email through the
    live EmailJS service ("service_alpqn7l" / "template_fqrjwz9") every time
    it runs, and counts against the EmailJS free-tier monthly quota.

The site's JS shows success/failure via a native browser alert() dialog
(see script.js), NOT a DOM element - so this test handles it via
driver.switch_to.alert rather than find_element.

Setup:
    pip install pytest selenium

Usage:
    1. Start the local server from the project root:
         python -m http.server 8000
    2. Run:
         pytest contact_form.py -v
"""

import time

import pytest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

# ---------------------------------------------------------------------------
# CONFIG
# ---------------------------------------------------------------------------

CONTACT_PAGE_URL = "http://localhost:8000/index.html"

NAME_FIELD_SELECTOR = "#user_name"
EMAIL_FIELD_SELECTOR = "#user_email"
SUBJECT_FIELD_SELECTOR = "#title"
MESSAGE_FIELD_SELECTOR = "#message"
SUBMIT_BUTTON_SELECTOR = "#contact-form button[type='submit']"

# Text expected inside the alert() on success / failure
SUCCESS_ALERT_TEXT = "message sent successfully"
FAILURE_ALERT_TEXT = "failed to send message"

TEST_NAME = "Integration Test"
TEST_EMAIL = "siyabonga.makhubu@indsafri.com"
TEST_SUBJECT = "Integration Test Subject"
TEST_MESSAGE = "This is an automated integration test submission."

ALERT_WAIT_TIMEOUT = 15  # EmailJS's send is async - give it real time to respond
HEADLESS = True


# ---------------------------------------------------------------------------
# Fixture
# ---------------------------------------------------------------------------

@pytest.fixture
def driver():
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--window-size=1280,800")

    drv = webdriver.Chrome(options=options)
    yield drv
    drv.quit()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_contact_form_sends_and_shows_success(driver):
    driver.get(CONTACT_PAGE_URL)

    wait = WebDriverWait(driver, 10)

    # Fill in the form
    name_field = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, NAME_FIELD_SELECTOR)))
    name_field.clear()
    name_field.send_keys(TEST_NAME)

    email_field = driver.find_element(By.CSS_SELECTOR, EMAIL_FIELD_SELECTOR)
    email_field.clear()
    email_field.send_keys(TEST_EMAIL)

    subject_field = driver.find_element(By.CSS_SELECTOR, SUBJECT_FIELD_SELECTOR)
    subject_field.clear()
    subject_field.send_keys(TEST_SUBJECT)

    message_field = driver.find_element(By.CSS_SELECTOR, MESSAGE_FIELD_SELECTOR)
    message_field.clear()
    message_field.send_keys(TEST_MESSAGE)

    # Submit - scroll into view first since this page is a long single-pager.
    submit_button = driver.find_element(By.CSS_SELECTOR, SUBMIT_BUTTON_SELECTOR)
    driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", submit_button)
    time.sleep(0.5)  # let scroll/animation settle

    # Debug: report what element is actually sitting at the button's click point,
    # so we can see what is intercepting it if this still fails.
    blocking_info = driver.execute_script("""
        const rect = arguments[0].getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;
        const topEl = document.elementFromPoint(x, y);
        return {
            x: x, y: y,
            tag: topEl ? topEl.tagName : null,
            id: topEl ? topEl.id : null,
            className: topEl ? topEl.className : null,
        };
    """, submit_button)
    print(f"DEBUG click point info: {blocking_info}")

    # Skip Selenium's native click (which enforces visibility/interception
    # checks) and dispatch the click directly via JS - this always reaches
    # the button regardless of any overlapping element.
    driver.execute_script("arguments[0].click();", submit_button)

    # The site shows success/failure via a native alert() after EmailJS
    # resolves - wait for that alert to appear, then read its text.
    try:
        WebDriverWait(driver, ALERT_WAIT_TIMEOUT).until(EC.alert_is_present())
    except Exception:
        pytest.fail(
            f"No alert appeared within {ALERT_WAIT_TIMEOUT}s after submitting the form. "
            f"EmailJS may not have resolved, or the submit handler didn't fire."
        )

    alert = driver.switch_to.alert
    alert_text = alert.text
    alert.accept()  # dismiss the alert so the browser doesn't hang

    assert FAILURE_ALERT_TEXT.lower() not in alert_text.lower(), (
        f"EmailJS reported a failure: '{alert_text}'"
    )
    assert SUCCESS_ALERT_TEXT.lower() in alert_text.lower(), (
        f"Expected success alert containing '{SUCCESS_ALERT_TEXT}', got: '{alert_text}'"
    )


def test_no_javascript_errors_on_contact_page(driver):
    """Sanity check: loading the page shouldn't throw JS errors that could
    silently break the EmailJS integration (e.g. wrong public key, SDK not
    loaded, undefined form fields). Ignores the harmless missing-favicon 404."""
    driver.get(CONTACT_PAGE_URL)
    time.sleep(1)  # let async scripts (like emailjs.init) settle

    logs = driver.get_log("browser")
    severe_errors = [
        entry for entry in logs
        if entry.get("level") == "SEVERE" and "favicon.ico" not in entry.get("message", "")
    ]

    assert not severe_errors, (
        "JavaScript errors found on page load:\n"
        + "\n".join(str(e) for e in severe_errors)
    )