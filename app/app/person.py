from typing import Optional



class Person:
    def __init__(
        self,
        *,
        first_name: Optional[str] = None,
        last_name: Optional[str] = None,
        address: Optional[str] = None,
        phone_number: Optional[str] = None,
    ):

        self._first_name = first_name
        self._last_name = last_name
        self._address = address
        self._phone_number = phone_number


    @property
    def first_name(self) -> Optional[str]:
        return self._first_name

    @property
    def last_name(self) -> Optional[str]:
        return self._last_name

    @property
    def address(self) -> Optional[str]:
        return self._address

    @property
    def phone_number(self) -> Optional[str]:
        return self._phone_number