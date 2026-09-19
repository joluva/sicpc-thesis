# Modulo para gestionar los log del sistema

import logging
import logging.handlers
import os
from dotenv import load_dotenv

load_dotenv()

PAPERTRAIL_HOST = os.getenv("PAPERTRAIL_HOST")
PAPERTRAIL_PORT = os.getenv("PAPERTRAIL_PORT")


def get_logger(component_name: str) -> logging.Logger:
    
    # Logger centralizado para el proyecto SICPC.
    # Envía eventos a Papertrail (si está configurado) y también a consola.
    
    logger = logging.getLogger(component_name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            f"%(asctime)s sicpc-{component_name}: %(levelname)s %(message)s",
            datefmt="%b %d %H:%M:%S",
        )

        # Consola (siempre activo, útil en desarrollo local)
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # Papertrail (solo si está configurado)
        if PAPERTRAIL_HOST and PAPERTRAIL_PORT:
            syslog_handler = logging.handlers.SysLogHandler(
                address=(PAPERTRAIL_HOST, int(PAPERTRAIL_PORT))
            )
            syslog_handler.setFormatter(formatter)
            logger.addHandler(syslog_handler)

    return logger