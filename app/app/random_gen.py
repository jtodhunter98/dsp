from mimesis import Generic

from .person import Person

gen = Generic("en", seed=0xFF)

def person_entry():
    return Person(
        first_name = gen.person.first_name(),
        last_name = gen.person.last_name(),
        address = gen.address.address(),
        phone_number = gen.person.telephone()
    )