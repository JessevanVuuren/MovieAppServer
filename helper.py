from logging.config import dictConfig
from pydantic import BaseModel
from typing import ClassVar
import datetime
import logging
import time


def send_response(success, status, error, payload):
    return { "success": success, "status": status, "error": error, "payload": payload }


class LogConfig(BaseModel):
    """Logging configuration to be set for the server"""
    LOGGER_NAME: str = "mycoolapp"
    LOG_FORMAT: str = "%(levelprefix)s | %(asctime)s | %(message)s"
    LOG_FORMAT: str = "%(levelprefix)s %(message)s"
    LOG_LEVEL: str = "DEBUG"

    # Logging config
    version: int = 1
    disable_existing_loggers: bool = False
    formatters: dict = {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": LOG_FORMAT,
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
    }
    handlers: dict = {
        "default": {
            "formatter": "default",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
        },
    }
    loggers: dict = {
        LOGGER_NAME: {"handlers": ["default"], "level": LOG_LEVEL},
    }


dictConfig(LogConfig().dict())
logger = logging.getLogger("mycoolapp")


def connection_ban(list:dict[str, dict[int, int]], host_ip:str, reset=False):
    if (host_ip not in list.keys() or reset):
        list[host_ip] = {"count": 0, "new_time": int(time.time()), "ban_time": None}
        return
    
    list[host_ip]["count"] += 1;
    ban_time = datetime.datetime.fromtimestamp(list[host_ip]["new_time"])
    match(list[host_ip]["count"]):
        case 4:
            list[host_ip]["new_time"] = (ban_time + datetime.timedelta(minutes=1)).timestamp()
            list[host_ip]["ban_time"] = "1 minute"
        case 5: 
            list[host_ip]["new_time"] = (ban_time + datetime.timedelta(minutes=5)).timestamp()
            list[host_ip]["ban_time"] = "5 minutes"
        case 6: 
            list[host_ip]["new_time"] = (ban_time + datetime.timedelta(minutes=10)).timestamp()
            list[host_ip]["ban_time"] = "10 minutes"
        case 7: 
            list[host_ip]["new_time"] = (ban_time + datetime.timedelta(minutes=30)).timestamp()
            list[host_ip]["ban_time"] = "30 minutes"
        case 8: 
            list[host_ip]["new_time"] = (ban_time + datetime.timedelta(hours=2)).timestamp()
            list[host_ip]["ban_time"] = "2 hours"
        case 9: 
            list[host_ip]["new_time"] = (ban_time + datetime.timedelta(hours=5)).timestamp()
            list[host_ip]["ban_time"] = "5 hours"
        case _ if (list[host_ip]["count"] > 10): 
            list[host_ip]["new_time"] = (ban_time + datetime.timedelta(days=1)).timestamp()
            list[host_ip]["ban_time"] = "1 day"

    # ban_time = ban_time + datetime.timedelta(seconds=10 * list[host_ip]["count"] ** 2)
    # list[host_ip]["ban_time"] = ban_time.timestamp()