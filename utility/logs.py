
import json
import logging
import os

FLASK_ENV = os.environ.get("FLASK_ENV", 'prod')


class StackdriverFormatter(logging.Formatter):

    def __init__(self, *args, **kwargs):
        """GCP StackdriverFormatter"""
        super(StackdriverFormatter, self).__init__(*args, **kwargs)

    def format(self, record):

        log_data = {
            'severity': record.levelname,
            'message': f"{record.filename} - {record.funcName}() line: {record.lineno} - {record.getMessage()}",
            'name': record.name,
            "function_name": f"{record.filename} - {record.funcName}() line: {record.lineno}",
            "unique_key": record.unique_key if record.unique_key else record.thread
        }

        return json.dumps(log_data)


def setup_log(unique_key=None, module_name=__name__, log_level="DEBUG"):
    """
    :param module_name:
    :param log_level:
    :param unique_key:
    return logger
    """

    logger_inner = logging.getLogger(module_name)
    logger_inner.propagate = False

    extra = {'unique_key': unique_key}
    handler = logging.StreamHandler()

    if FLASK_ENV != 'development':
        formatter = StackdriverFormatter()
        handler.setFormatter(formatter)

    else:
        if unique_key:
            format_message = '%(levelname)-8s- <[%(unique_key)25s]> - %(funcName)20s():%(lineno)4s- %(message)s'
        else:
            format_message = '%(levelname)-8s- %(funcName)20s():%(lineno)4s- %(message)s'
        formatter = logging.Formatter(format_message)
        handler.setFormatter(formatter)

    logger_inner.addHandler(handler)
    logger_inner = logging.LoggerAdapter(logger_inner, extra)
    logger_inner.setLevel(log_level)

    return logger_inner
