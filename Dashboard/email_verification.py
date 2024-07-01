"""utility functions to add unverified email to ses and send verification emails."""

import logging

from dotenv import load_dotenv
from botocore.exceptions import ClientError
from mypy_boto3_ses.client import SESClient as ses_client

from helpers import is_ses


def send_verification_email(boto_ses_client: ses_client, email: str) -> dict[bool, str]:
    """adds email as unverified email to ses and send a verification email.
    Returns a dictionary containing fields:
            success    : True if sending email verification was a success, else False
            reason     : If success is False, return a reason for failure
            error      : If success is False, return an error object (only if types are correct)
            request_id : If success is True, return a request id for that email verification.
    """
    if not isinstance(email, str):
        logging.error(
            "send_verification_email passed `email` argument not of type str.")
        return {"success": False, "reason": "bad email type, email must be of type str."}
    if not is_ses(boto_ses_client):
        logging.error(
            "send_verification_email client is not a boto3 ses client.")
        return {"success": False, "reason": "client is not a boto3 ses client."}
    logging.info("Sending email verification...")
    try:
        response = boto_ses_client.verify_email_identity(EmailAddress=email)
    except ClientError as e:
        if not e.response.get("Error"):
            logging.error("sending email verification failed due to an unknown reason\
 (no Error attribute on response object), see field \"error\"!")
            reason = "unknown reason, but no Error attribute on response, see field \"error\"!"
        elif e.response["Error"].get("Code") == "InvalidClientTokenId":
            logging.error(
                "sending email verification failed due to bad aws credentials!")
            reason = "bad aws credentials!"
        elif e.response["Error"].get("Code") == "InvalidParameterValue":
            logging.error(
                "sending email verification failed due to bad email address format!")
            reason = "invalid email address format."
        else:
            logging.error(
                "sending email verification failed due to an unknown reason!")
            reason = "failure for unknown reason, see field \"error\""
        return {"success": False, "reason": reason, "error": e.response}
    logging.info("Sending email verification success!")
    return {"success": True, "request_id": response["ResponseMetadata"].get("RequestId")}


def unverify_email(boto_ses_client: ses_client, email: str) -> None:
    """Remove a verified email from ses. Upon failure, return None.
    This is functionality to be seen and used on the frontend, thus
    failing is unacceptable."""
    if not isinstance(email, str):
        logging.error(
            "unverify_email passed `email` argument not of type str.")
        return None
    if not is_ses(boto_ses_client):
        logging.error(
            "unverify_email client is not a boto3 ses client.")
        return None
    logging.info("Removing verified email...")
    try:
        boto_ses_client.delete_verified_email_address(
            EmailAddress=email
        )
        logging.info("unverity_email completed successfully, removing email.")
    except Exception:
        logging.error("unverify_email client failed unexpectedly.")
    return None


if __name__ == "__main__":
    load_dotenv()
    logging.basicConfig(level="INFO")
