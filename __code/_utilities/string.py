def get_beginning_common_part_of_string_from_list(list_of_text=None, filename_spacer='_'):
	"""This method returns the continuous part of a string, from the beginning, that can be found
	in all string provided. The match will stop before the last filename_spacer

	for example:
	list_of_text = ['abc_000.txt', 'abc_001.txt', 'abc_002.txt']
	the method will return 'abc_'
	"""
	if list_of_text is None:
		raise ValueError("Please provide a list of string!")

	split_list_of_text = [text.split(filename_spacer) for text in list_of_text]

	def intersection(lst1, lst2):
		return [item for item in lst1 if item in lst2]

	list_reference = split_list_of_text[0]
	for _list in split_list_of_text[1:]:
		list_reference = intersection(list_reference, _list)

	return filename_spacer.join(list_reference)