import os
import logging
import re
from typing import Dict, Any
import requests

logger = logging.getLogger(__name__)

ZAPI_BASE_URL = os.getenv("ZAPI_BASE_URL", "https://api.z-api.io")
ZAPI_INSTANCE_ID = os.getenv("ZAPI_INSTANCE_ID", "")
ZAPI_TOKEN = os.getenv("ZAPI_TOKEN", "")
ZAPI_TIMEOUT = float(os.getenv("ZAPI_TIMEOUT_SECONDS", "10"))
ZAPI_CLIENT_TOKEN = os.getenv("ZAPI_CLIENT_TOKEN", "")


def _normalize_phone_for_zapi(phone: str) -> str:
    if not phone:
        return ""
    digits = re.sub(r"\D", "", phone)
    # Z-API expects country code, ensure BR +55 if missing and number looks Brazilian with 10-11 digits
    if digits.startswith("55"):
        return digits
    if len(digits) in (10, 11):
        return f"55{digits}"
    return digits


def _zapi_url(path: str) -> str:
    if not (ZAPI_INSTANCE_ID and ZAPI_TOKEN):
        raise RuntimeError("Configure ZAPI_INSTANCE_ID and ZAPI_TOKEN in environment")
    return f"{ZAPI_BASE_URL}/instances/{ZAPI_INSTANCE_ID}/token/{ZAPI_TOKEN}{path}"


def _zapi_send_text(phone: str, message: str) -> Dict[str, Any]:
    # Build URL and gracefully handle missing configuration
    try:
        url = _zapi_url("/send-text")
    except Exception as e:
        logger.error("Z-API configuration error: %s", e)
        return {"success": False, "error": str(e)}
    payload = {"phone": phone, "message": message}
    headers = {"Content-Type": "application/json"}
    # Some Z-API setups require a Client-Token header in addition to the URL token
    if ZAPI_CLIENT_TOKEN:
        headers["Client-Token"] = ZAPI_CLIENT_TOKEN
    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=ZAPI_TIMEOUT)
        ok = 200 <= resp.status_code < 300
        if not ok:
            logger.warning("Z-API non-2xx: %s body=%s", resp.status_code, resp.text)
        body = _safe_json(resp)
        error_msg = None
        if not ok:
            # Try to surface meaningful error message
            error_msg = body.get("error") if isinstance(body, dict) else None
        return {
            "success": ok,
            "status": resp.status_code,
            "body": body,
            "error": error_msg,
        }
    except Exception as e:
        logger.error("Error calling Z-API: %s", e)
        return {"success": False, "error": str(e)}


def _safe_json(resp):
    try:
        return resp.json()
    except Exception:
        return {"raw": resp.text}


def _build_scheduled_message(interview) -> str:
    candidate_name = getattr(interview.candidate, "full_name", "")
    date_str = interview.scheduled_date.strftime("%d/%m/%Y") if interview.scheduled_date else ""
    time_str = interview.scheduled_time.strftime("%H:%M") if interview.scheduled_time else ""
    location = interview.location or ""
    tipo_display = getattr(interview, "get_interview_type_display", None)
    tipo = interview.get_interview_type_display() if callable(tipo_display) else (interview.interview_type or "")
    duracao = interview.duration_minutes or 60

    lines = [
        "*Entrevista Agendada - Pinte Pinturas*",
        "",
        f"Olá {candidate_name}! 👋",
        "",
        "Sua entrevista foi agendada com sucesso! ✅",
        "",
        "*📋 Detalhes da Entrevista:*",
        f"• Tipo: {tipo}",
        f"• 📅 Data: {date_str}",
        f"• ⏰ Horário: {time_str}",
        f"• ⏳ Duração: {duracao} minutos",
    ]
    if location:
        lines.append(f"• 📍 Local/Link: {location}")
    lines.extend([
        "",
        "📌 Por favor, chegue com 10 minutos de antecedência.",
        "🍀 Boa sorte! Estamos ansiosos para conhecê-lo(a)!",
        "",
        "Pinte Pinturas - Equipe de RH",
    ])
    return "\n".join(lines)


def _build_rescheduled_message(interview, old_date, old_time) -> str:
    date_str = interview.scheduled_date.strftime("%d/%m/%Y") if interview.scheduled_date else ""
    time_str = interview.scheduled_time.strftime("%H:%M") if interview.scheduled_time else ""
    old_date_str = old_date.strftime("%d/%m/%Y") if old_date else ""
    old_time_str = old_time.strftime("%H:%M") if old_time else ""
    location = interview.location or ""
    candidate_name = getattr(interview.candidate, "full_name", "")

    lines = [
        "*Entrevista Reagendada - Pinte Pinturas*",
        "",
        f"Olá {candidate_name}!",
        "",
        "Sua entrevista foi reagendada:",
        "",
        "*❌ Data anterior:*",
        f"• {old_date_str} às {old_time_str}",
        "",
        "*✅ Nova data:*",
        f"• Data: {date_str}",
        f"• Horário: {time_str}",
    ]
    if location:
        lines.append(f"• Local/Link: {location}")
    lines.extend([
        "",
        "Agradecemos sua compreensão!",
        "",
        "Pinte Pinturas - Equipe de RH",
    ])
    return "\n".join(lines)


def send_interview_scheduled_via_zapi(interview) -> Dict[str, Any]:
    phone_raw = getattr(interview.candidate, "phone_number", "")
    phone = _normalize_phone_for_zapi(phone_raw)
    if not phone:
        return {"success": False, "error": "candidate phone missing"}
    message = _build_scheduled_message(interview)
    return _zapi_send_text(phone, message)


def send_interview_rescheduled_via_zapi(interview, old_date, old_time) -> Dict[str, Any]:
    phone_raw = getattr(interview.candidate, "phone_number", "")
    phone = _normalize_phone_for_zapi(phone_raw)
    if not phone:
        return {"success": False, "error": "candidate phone missing"}
    message = _build_rescheduled_message(interview, old_date, old_time)
    return _zapi_send_text(phone, message)


def _build_cancelled_message(interview) -> str:
    candidate_name = getattr(interview.candidate, "full_name", "")
    date_str = interview.scheduled_date.strftime("%d/%m/%Y") if interview.scheduled_date else ""
    time_str = interview.scheduled_time.strftime("%H:%M") if interview.scheduled_time else ""

    lines = [
        "*Entrevista Cancelada - Pinte Pinturas*",
        "",
        f"Olá {candidate_name}.",
        "",
        "Sua entrevista foi cancelada. ❌",
        "",
        "*Detalhes:*",
        f"• Data: {date_str}",
        f"• Horário: {time_str}",
        "",
        "Se necessário, entraremos em contato para reagendar.",
        "",
        "Pinte Pinturas - Equipe de RH",
    ]
    return "\n".join(lines)


def send_interview_cancelled_via_zapi(interview) -> Dict[str, Any]:
    phone_raw = getattr(interview.candidate, "phone_number", "")
    phone = _normalize_phone_for_zapi(phone_raw)
    if not phone:
        return {"success": False, "error": "candidate phone missing"}
    message = _build_cancelled_message(interview)
    return _zapi_send_text(phone, message)


def send_text_to_phone(phone_raw: str, message: str) -> Dict[str, Any]:
    """Send a plain WhatsApp text message to a phone number via Z-API.
    phone_raw may contain formatting; we normalize for Z-API.
    """
    phone = _normalize_phone_for_zapi(phone_raw)
    if not phone:
        return {"success": False, "error": "phone missing"}
    if not message:
        return {"success": False, "error": "message empty"}
    return _zapi_send_text(phone, message)
