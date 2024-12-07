import logging
from colorama import Fore, Style, Back

class ColoredFormatter(logging.Formatter):
    def format(self, record):
        levelname_color = {
            'DEBUG': Fore.CYAN + Style.BRIGHT,
            'INFO': Fore.GREEN + Style.BRIGHT,
            'WARNING': Fore.YELLOW + Style.BRIGHT,
            'ERROR': Fore.RED + Style.BRIGHT,
            'CRITICAL': Fore.RED + Style.BRIGHT,
        }
        message = super().format(record)
        if record.levelname in levelname_color:
            message = levelname_color[record.levelname] + message + Style.RESET_ALL
        return message


class CustomLogger:
    def __init__(self):
        self.log_file = 'log/test.txt'
        self.logger = logging.getLogger('Stocklogger')
        self.logger.setLevel(logging.DEBUG)

        
        file_handler = logging.FileHandler(self.log_file)
        file_handler.setLevel(logging.DEBUG)
        plain_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(plain_formatter)

        
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.DEBUG)
        colored_formatter = ColoredFormatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        console_handler.setFormatter(colored_formatter)

        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)


log = CustomLogger()
