import json
from dataclasses import dataclass
from math import isfinite


@dataclass(frozen=True)
class SensorReadingDTO:
    temp: float
    hum: float

    @classmethod
    def from_json(cls, payload: bytes) -> "SensorReadingDTO":
        data = json.loads(payload.decode("utf-8"))
        if not isinstance(data, dict):
            raise ValueError("MQTT payload must be a JSON object.")

        values = {}
        for field in ("temp", "hum"):
            value = data.get(field)
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError(f"MQTT payload field '{field}' must be numeric.")
            try:
                number = float(value)
            except OverflowError as exc:
                raise ValueError(f"MQTT payload field '{field}' must be finite.") from exc
            if not isfinite(number):
                raise ValueError(f"MQTT payload field '{field}' must be finite.")
            values[field] = number

        return cls(**values)
