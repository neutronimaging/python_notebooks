def key_path_exists_in_dictionary(dictionary=None, tree_key=None):
	"""this method checks if full key path in the dictionary exists"""
	top_dictionary = dictionary
	for _key in tree_key:
		if top_dictionary.get(_key, None) is None:
			return False
		top_dictionary = top_dictionary.get(_key)
	return True
