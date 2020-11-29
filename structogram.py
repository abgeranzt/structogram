#stdlib
import argparse
import re
import sys
import yaml

def get_args():
	parser = argparse.ArgumentParser()
	parser.add_argument('-f', '--file', help='input file', required=True)
	parser.add_argument('-o', '--output', help='output file')
	return parser.parse_args()

def parse_yaml(path):
	# Read yaml file and return contents as dict
	try:
		with open(path, 'r') as f:
			tree = yaml.safe_load(f)
			f.close()
			return tree
	# Common user error, hide stack trace
	except FileNotFoundError as err:
		print(err)
		sys.exit(1)

def map_tree(root):
	# Recursively map tree structure
	tree = []
	for branch in root:
		# Branch is a compound statement:
		if type(branch) == dict:
			# list() and keys() glued together to get dict keys
			b_type = list(branch.keys())[0]
			b_root = branch[b_type]
			expr = list(b_root[0].keys())[0]
			body = map_tree(b_root[0][expr])
			# Statement is a condition: split body for optional 'else'
			if re.search('cond', b_type):
				body = {'true': body, 'false': None}
				# 'else' present:
				if len(b_root) == 2:
					body['false'] = map_tree(b_root[1]['else'])
			branch = {'type': b_type, 'expr': expr, 'body': body}
		tree.append(branch)
	return tree 

def main():
	args = get_args()
	tree = map_tree(parse_yaml(args.file))

if __name__ == '__main__':
	main()
