from dataclasses import dataclass


@dataclass(frozen=True)
class KeyValue:
    """
    Key-value pair class
    """
    key: str
    value: object = None


key_value = KeyValue(key="key")

print(key_value == KeyValue(key="key"))
print(str(key_value))
