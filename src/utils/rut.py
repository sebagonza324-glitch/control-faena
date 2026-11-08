"""Validación y normalización de RUT chileno."""


class RutInvalidoError(Exception):
    """Indica que el RUT no es válido."""


def calcular_dv(cuerpo: str) -> str:
    """Calcula el dígito verificador con módulo 11."""
    if not cuerpo or any(digito not in "0123456789" for digito in cuerpo):
        raise RutInvalidoError("El cuerpo del RUT debe contener solo dígitos.")

    suma = 0
    multiplicador = 2
    for digito in reversed(cuerpo):
        suma += int(digito) * multiplicador
        multiplicador = multiplicador + 1 if multiplicador < 7 else 2

    resultado = 11 - suma % 11
    if resultado == 11:
        return "0"
    if resultado == 10:
        return "K"
    return str(resultado)


def normalizar_rut(rut: str) -> str:
    """Valida un RUT y lo devuelve sin puntos y con guion."""
    if not isinstance(rut, str):
        raise RutInvalidoError("El RUT debe ser texto.")

    limpio = "".join(rut.split())
    if not limpio or any(
        caracter not in "0123456789.-kK" for caracter in limpio
    ):
        raise RutInvalidoError("El RUT contiene caracteres no válidos.")
    if limpio.count("-") > 1:
        raise RutInvalidoError("El formato del RUT no es válido.")

    if "-" in limpio:
        cuerpo_original, dv_original = limpio.split("-")
        if not dv_original or "." in dv_original or len(dv_original) != 1:
            raise RutInvalidoError("El formato del RUT no es válido.")
        cuerpo = cuerpo_original.replace(".", "")
        dv = dv_original.upper()
    else:
        compacto = limpio.replace(".", "")
        if len(compacto) < 2:
            raise RutInvalidoError("El formato del RUT no es válido.")
        cuerpo, dv = compacto[:-1], compacto[-1].upper()

    if not cuerpo.isdigit() or not 7 <= len(cuerpo) <= 8:
        raise RutInvalidoError("El cuerpo del RUT debe tener 7 u 8 dígitos.")
    if dv != calcular_dv(cuerpo):
        raise RutInvalidoError("El dígito verificador del RUT no coincide.")

    return f"{cuerpo}-{dv}"
