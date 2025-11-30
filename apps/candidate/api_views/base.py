"""
Base imports and utilities for API views.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Count, Q
from django.http import HttpResponse
from datetime import datetime, timedelta
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)
