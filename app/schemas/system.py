# File: app/schemas/system.py
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Union

class ConfigUpdate(BaseModel):
    """Payload for dynamic system configuration updates."""
    config_value: Union[Dict[str, Any], List[Any]] = Field(
        ..., 
        description="The new configuration payload to be persisted in the main database."
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "config_value": {
                    "base_fee": 150000,
                    "surge_pricing_active": False,
                    "supported_regions": ["ID-JKT", "ID-BDO"]
                }
            }
        }
    }