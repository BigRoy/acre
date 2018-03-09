import unittest

import env_prototype.api as api


class TestDynamicEnvironments(unittest.TestCase):

    def test_parse_platform(self):
        """Parse works for 'platform-specific environments'"""

        data = {
            "A": {
                "darwin": "darwin-path",
                "windows": "windows-path",
                "linux": "linux-path"
            },
            "B": "universal"
        }

        result = api.parse(data, platform_name="darwin")
        self.assertEqual(result["A"], data["A"]["darwin"])
        self.assertEqual(result["B"], data["B"])

        result = api.parse(data, platform_name="windows")
        self.assertEqual(result["A"], data["A"]["windows"])
        self.assertEqual(result["B"], data["B"])

        result = api.parse(data, platform_name="linux")
        self.assertEqual(result["A"], data["A"]["linux"])
        self.assertEqual(result["B"], data["B"])

    def test_nesting_deep(self):
        """Deep nested dynamic environment computes correctly"""

        data = {
            "A": "bla",
            "B": "{A}",
            "C": "{B}",
            "D": "{A}{B}",
            "E": "{A}{B}{C}{D}",
            "F": "{D}",
            "G": "{F}_{E}",
            "H": "{G}",
            "I": "deep_{H}"
        }

        result = api.compute(data)

        self.assertEqual(result, {
            "A": "bla",
            "B": "bla",
            "C": "bla",
            "D": "blabla",
            "E": "blablablablabla",
            "F": "blabla",
            "G": "blabla_blablablablabla",
            "H": "blabla_blablablablabla",
            "I": "deep_blabla_blablablablabla"
        })

    def test_cycle(self):
        """Cycle error is correctly detected in dynamic environment"""
        data = {
            "X": "{Y}",
            "Y": "{X}"
        }

        with self.assertRaises(api.CycleError):
            api.compute(data, allow_cycle=False)

        # If we compute the cycle the result is unknown, it can be either {Y}
        # or {X} for both values so we just check whether are equal
        result = api.compute(data, allow_cycle=True)
        self.assertEqual(result["X"], result["Y"])

    def test_dynamic_keys(self):
        """Computing dynamic keys works"""
        data = {
            "A": "D",
            "B": "C",
            "{A}": "this is D",
            "{B}": "this is C"
        }

        env = api.compute(data)

        self.assertEqual(env, {
          "A": "D",
          "B": "C",
          "C": "this is C",
          "D": "this is D",
        })

    def test_dynamic_keys_clash_cycle(self):
        """Dynamic key clash cycle captured correctly"""
        data = {
            "foo": "foo",
            "{foo}": "bar"
        }

        with self.assertRaises(api.DynamicKeyClashError):
            api.compute(data, allow_key_clash=False)

        # Allow to pass (even if unpredictable result)
        api.compute(data, allow_key_clash=True)

    def test_dynamic_keys_clash(self):
        """Dynamic key clash captured correctly"""
        data = {
            "A": "foo",
            "{A}": "bar",
            "foo": "B"
        }

        with self.assertRaises(api.DynamicKeyClashError):
            api.compute(data, allow_key_clash=False)

        # Allow to pass (even if unpredictable result)
        api.compute(data, allow_key_clash=True)

    def test_compute_preserve_reference_to_self(self):
        """api.compute() does not format key references to itself"""

        data = {
            "PATH": "{PATH}",
            "PYTHONPATH": "x;y/{PYTHONPATH}"
        }
        data = api.compute(data)
        self.assertEqual(data, {
            "PATH": "{PATH}",
            "PYTHONPATH": "x;y/{PYTHONPATH}"
        })

    def test_append(self):
        """Append paths of two environments into one."""

        data_a = {
            "A": "A",
            "B": "B"
        }
        data_b = {
            "A": "A2",
            "C": "C2"
        }

        # Keep unaltered copies to check afterwards the originals
        # remain unaltered by the append function
        _data_a = data_a.copy()
        _data_b = data_b.copy()

        data = api.append(data_a, data_b)

        self.assertEqual(data, {
            "A": "A;A2",
            "B": "B",
            "C": "C2"
        })

        # Ensure the original dicts are unaltered
        self.assertEqual(data_a, _data_a)
        self.assertEqual(data_b, _data_b)

    def test_merge(self):
        """api.merge() merges correctly"""

        data = {
            "A": "a;{A}",
            "B": "b;c;d",
            "C": "C"
        }

        environment = {
            "A": "A",
            "C": "D"
        }

        data = api.merge(data, current_env=environment)

        # Note that C from the environment is not preserved, it's overwritten
        # by the merge. (To preserve it should have a reference to itself)
        # See "A"
        self.assertEqual(data, {
            "A": "a;A",
            "B": "b;c;d",
            "C": "C"
        })

    def test_merge_formats_references_to_self(self):
        """api.merge() correctly formats variables references to itself"""

        # Skip when not in current environment
        data = {
            "PATH": "a;b;{PATH}",
        }

        merged = api.merge(data, current_env={})
        self.assertEqual(merged["PATH"], "a;b;")

        # Allow merge
        data = {
            "PATH": "a;b;{PATH}"
        }

        # Note that on merge the paths are *not* ensured to be unique and
        # *might* end up in the resulting variable more than once.
        # This is expected behavior.
        merged = api.merge(data, current_env={"PATH": "b;c;d"})
        self.assertEqual(merged["PATH"], "a;b;b;c;d")
