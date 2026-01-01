from __code.resonance_fitting import Parent


class Get(Parent):
    def full_name_of_element_from_abreviation(self, abbreviation: str) -> str:
        """Get the full name of an element from its abbreviation.

        Args:
            abbreviation (str): The abbreviation of the element (e.g., 'H' for Hydrogen).

        Returns:
            str: The full name of the element.
        """
        dict_elements = self.parent.dict_elements
        for _element_name in dict_elements.keys():
            _abbreviation = dict_elements[_element_name]["symbol"]
            if _abbreviation == abbreviation:
                return _element_name
        raise ValueError(f"Element with abbreviation '{abbreviation}' not found.")
