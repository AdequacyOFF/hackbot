from dataclasses import dataclass

# Нотация: "<key>:<id>"
def pack(key: str, value: int | str) -> str:
    return f"{key}:{value}"

def unpack(data: str) -> tuple[str, str]:
    k, v = data.split(":", 1)
    return k, v