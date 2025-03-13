import os
from loguru import logger

class LoggerConfig:
    def __init__(self, log_dir="logs", log_file="proxy.log", rotation="10MB", level="INFO"):
        self.log_dir = log_dir
        self.log_file = log_file
        self.rotation = rotation
        self.level = level

    def setup_logger(self):
        """Configura il logger per l'applicazione."""
        # Crea la cartella logs se non esiste
        if not os.path.exists(self.log_dir):
            os.makedirs(self.log_dir)

        # Imposta il percorso completo per il file di log
        log_path = os.path.join(self.log_dir, self.log_file)

        logger.remove()  # Rimuove qualsiasi configurazione precedente del logger
        logger.add(log_path, rotation=self.rotation, level=self.level)
        return logger
