from typing import Tuple, Optional
import json
from schemas.schema import MessageInput
from pydantic import ValidationError
import logging

logger = logging.getLogger(__name__)


class MessageValidator:
    @staticmethod
    def validate_message(
        data: str,
    ) -> Tuple[bool, Optional[MessageInput], Optional[str]]:
        """
        Validate the incoming WebSocket message.

        Args:
            data (str): The raw message data from WebSocket

        Returns:
            Tuple[bool, Optional[MessageInput], Optional[str]]:
            - Boolean indicating if validation passed
            - Validated MessageInput model if successful, None if failed
            - Error message if validation failed, None if successful
        """
        try:
            try:
                message_data = json.loads(data)
            except json.JSONDecodeError as e:
                return False, None, f"Invalid JSON format: {str(e)}"

            validated_data = MessageInput(**message_data)
            return True, validated_data, None

        except ValidationError as e:
            errors = []
            for error in e.errors():
                field = error["loc"][0]
                msg = error["msg"]
                errors.append(f"{field}: {msg}")
            error_message = "; ".join(errors)
            logger.warning(f"Message validation failed: {error_message}")
            return False, None, error_message

        except Exception as e:
            logger.error(f"Unexpected error during message validation: {str(e)}")
            return False, None, f"Internal validation error: {str(e)}"
