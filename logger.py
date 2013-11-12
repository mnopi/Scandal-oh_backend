# -*- coding: utf-8 -*-

from services.models import LogEntry

class Logger:
    @staticmethod
    def warning(message):
        LogEntry.objects.create(category=LogEntry.WARNING, message=message)

    @staticmethod
    def debug(message):
        LogEntry.objects.create(category=LogEntry.DEBUG, message=message)

    @staticmethod
    def info(message):
        LogEntry.objects.create(category=LogEntry.INFO, message=message)

    @staticmethod
    def error(message):
        LogEntry.objects.create(category=LogEntry.ERROR, message=message)

    @staticmethod
    def critical(message):
        LogEntry.objects.create(category=LogEntry.CRITICAL, message=message)

