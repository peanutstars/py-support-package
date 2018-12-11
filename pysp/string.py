import os
import re


class KeyExpander:

    # Reference: https://stackoverflow.com/a/30777398
    @classmethod
    def environ_vars(cls, string, default=None, skip_escaped=False):
        """Expand environment variables of form $var and ${var}.
           If parameter 'skip_escaped' is True, all escaped variable references
           (i.e. preceded by backslashes) are skipped.
           Unknown variables are set to 'default'. If 'default' is None,
           they are left unchanged.
        """
        def replace_var(m):
            defvalue = m.group(0) if default is None else default
            # print(m.group(2), m.group(1))
            return os.environ.get(m.group(2) or m.group(1), defvalue)

        reval = (r'(?<!\\)' if skip_escaped else '') + r'\$(\w+|\{([^}]*)\})'
        return re.sub(reval, replace_var, string)
