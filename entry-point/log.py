from datetime import date, datetime


class Logger:
    def __init__(self, log_file_name="entry-point.log"):
        self.log_file = open(log_file_name,"w+")

    def info(self, message: str):
        self.__write(message=f"    INFO    __________ {message} {'_'*(80-len(message))} {datetime.now()}")
    def err(self, message: str):
        self.__write(message=f"    ERR    ___________ {message} {'_'*(80-len(message))} {datetime.now()}")
    def debug(self, message:str):
        self.__write(message=f"    DBUG    __________ {message} {'_'*(80-len(message))} {datetime.now()}")
    def __write(self, message):
        print(message)
        self.log_file.write(message+"\n")
        self.log_file.flush()