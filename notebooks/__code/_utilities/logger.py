import logging
import os


def display_dictionary_in_logging(dictionary):
    for key, value in dictionary.items():
        logging.info(f"\t {key}: {value}")
    logging.info("")  # Add an empty line for better readability


def setup_logging(basename_of_log_file: str = "") -> str:
    """
    Set up logging configuration for the CT reconstruction pipeline.

    Creates a log file with the user's name and script name, configures
    logging format and level. Attempts to use a shared log directory
    but falls back to user's home directory if needed.

    Args:
        basename_of_log_file: Base name for the log file (usually script name)

    Returns:
        Full path to the created log file

    Note:
        Log files are created with write mode ('w'), so they overwrite
        existing logs from the same script.
    """
    USER_NAME: str = os.getlogin()  # add user name to the log file name

    default_path: str = "/SNS/VENUS/shared/log/"
    if os.path.exists(default_path) is False:
        # user home folder
        default_path = os.path.join(os.path.expanduser("~"), "log")
    if not os.path.exists(default_path):
        os.makedirs(default_path)

    log_file_name: str = os.path.join(
        default_path, f"{basename_of_log_file}_{USER_NAME}.log"
    )

    # Remove existing handlers so we can redirect to a new file
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        handler.close()

    file_handler = logging.FileHandler(log_file_name, mode="w")
    file_handler.setFormatter(
        logging.Formatter("[%(levelname)s] - %(asctime)s - %(message)s")
    )
    root_logger.addHandler(file_handler)

    logging.info(f"*** Starting a new script {basename_of_log_file} ***")

    print(f"logging file: {log_file_name}")

    return log_file_name
