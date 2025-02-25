import logging

from dispatcher.logging.configure_logging import configure_logging

logger = logging.getLogger(__name__)


def startup():
    """Perform application startup actions"""
    configure_logging("production")


def main():
    """Main entry point"""
    startup()
    logger.info("Hello, world!")


if __name__ == "__main__":
    main()
