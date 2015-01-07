def tree_to_str(root, indent_depth=4, start_indent=0, indent=' ', accessor='__iter__'):
    new_indent = indent_depth + start_indent
    print(indent * new_indent + repr(root))
    if hasattr(root, accessor):
        for item in getattr(root, accessor):
            print_tree(item, indent_depth, new_indent, indent, accessor)


def print_tree(root, indent_depth=4, start_indent=0, indent=' ', accessor='__iter__', file=None):
    s = tree_to_str(root, indent_depth, start_indent, indent, accessor)
    if file is None:
        print(s)
    else:
        print(s, file=file)
