def build_set_from_file(cls, sourcefile, fb_filter_idx=None):
    # Generic build set of objects from a file of objects
    items = {}
    with open(sourcefile, 'r') as f:
        for line in f:
            columns = line.strip().split(',')
            if fb_filter_idx and columns[fb_filter_idx] == "None":
                continue
            item = cls(columns)
            items[item.id] = item
    return items

def build_instance(self, attribute_list, data):
    # Takes in a list of column names and values for those columns,
    # saves as attributes on a class instance
    if len(attribute_list) != len(data):
        raise "Lengths do not match.  Expected attributes: %s, data: %s" % (len(attribute_list), len(data))
    for i in range(len(attribute_list)):
        command = build_command_for(attribute_list[i], data[i])
        exec(command)

def build_command_for(attr_name, item):
    if item == "None" or item[0].isdigit():
        return "self.%s = %s" % (attr_name, item)
    else:
        return "self.%s = \"%s\"" % (attr_name, item)
