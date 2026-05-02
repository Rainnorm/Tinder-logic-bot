def validate_age(text: str):
    if not text.isdigit():
        return False, "Возраст должен быть числом"

    age = int(text)

    if age < 14:
        return False, "Минимальный возраст 14"
    if age > 100:
        return False, "Максимальный возраст 100"

    return True, age