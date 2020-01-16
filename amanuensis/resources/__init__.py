import pkg_resources

def get_stream(*path):
	rs_path = "/".join(path)
	return pkg_resources.resource_stream(__name__, rs_path)