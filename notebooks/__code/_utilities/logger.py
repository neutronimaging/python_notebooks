import logging


def display_dictionary_in_logging(dictionary):

    for key, value in dictionary.items():
        logging.info(f"\t {key}: {value}")
    logging.info("")  # Add an empty line for better readability
