from entities.message_type import MessageType


def test_message_type_values() -> None:
    """
    Comprueba que cada miembro tenga el valor
    esperado.
    """

    assert MessageType.DEFAULT == "default"
    assert MessageType.INFO == "info"
    assert MessageType.SUCCESS == "success"
    assert MessageType.WARNING == "warning"
    assert MessageType.ERROR == "error"


def test_message_type_is_str() -> None:
    """
    Comprueba que los miembros del enum sean
    instancias de str.
    """

    assert isinstance(MessageType.DEFAULT, str)
    assert isinstance(MessageType.INFO, str)
    assert isinstance(MessageType.SUCCESS, str)
    assert isinstance(MessageType.WARNING, str)
    assert isinstance(MessageType.ERROR, str)


def test_message_type_contains_all_members() -> None:
    """
    Comprueba que el enum contenga todos los
    miembros esperados.
    """

    assert list(MessageType) == [
        MessageType.DEFAULT,
        MessageType.INFO,
        MessageType.SUCCESS,
        MessageType.WARNING,
        MessageType.ERROR,
    ]


def test_message_type_can_be_created_from_value() -> None:
    """
    Comprueba que los miembros puedan
    recuperarse a partir de su valor.
    """

    assert MessageType("default") is MessageType.DEFAULT
    assert MessageType("info") is MessageType.INFO
    assert MessageType("success") is MessageType.SUCCESS
    assert MessageType("warning") is MessageType.WARNING
    assert MessageType("error") is MessageType.ERROR
