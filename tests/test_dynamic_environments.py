# -*- coding: utf-8 -*
"""Acre test suite."""
import unittest
from unittest import mock

import acre


class TestDynamicEnvironments(unittest.TestCase):
    """Test acre processing of dynamic environments."""

    def test_parse_platform(self):
        """Parse works for 'platform-specific environments'."""
        data = {
            "A": {
                "darwin": "darwin-path",
                "windows": "windows-path",
                "linux": "linux-path"
            },
            "B": "universal"
        }
        result = acre.parse(data, platform_name="darwin")
        self.assertEqual(result["A"], data["A"]["darwin"])
        self.assertEqual(result["B"], data["B"])

        result = acre.parse(data, platform_name="windows")
        self.assertEqual(result["A"], data["A"]["windows"])
        self.assertEqual(result["B"], data["B"])

        result = acre.parse(data, platform_name="linux")
        self.assertEqual(result["A"], data["A"]["linux"])
        self.assertEqual(result["B"], data["B"])

    def test_nesting_deep(self):
        """Deep nested dynamic environment computes correctly."""
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

        result = acre.compute(data)

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
        """Cycle error is correctly detected in dynamic environment."""
        data = {
            "X": "{Y}",
            "Y": "{X}"
        }

        with self.assertRaises(acre.CycleError):
            acre.compute(data, allow_cycle=False)

        # If we compute the cycle the result is unknown, it can be either {Y}
        # or {X} for both values so we just check whether are equal
        result = acre.compute(data, allow_cycle=True)
        self.assertEqual(result["X"], result["Y"])

    def test_dynamic_keys(self):
        """Computing dynamic keys works."""
        data = {
            "A": "D",
            "B": "C",
            "{A}": "this is D",
            "{B}": "this is C"
        }

        env = acre.compute(data)

        self.assertEqual(env, {
          "A": "D",
          "B": "C",
          "C": "this is C",
          "D": "this is D",
        })

    def test_dynamic_keys_clash_cycle(self):
        """Dynamic key clash cycle captured correctly."""
        data = {
            "foo": "foo",
            "{foo}": "bar"
        }

        with self.assertRaises(acre.DynamicKeyClashError):
            acre.compute(data, allow_key_clash=False)

        # Allow to pass (even if unpredictable result)
        acre.compute(data, allow_key_clash=True)

    def test_dynamic_keys_clash(self):
        """Dynamic key clash captured correctly."""
        data = {
            "A": "foo",
            "{A}": "bar",
            "foo": "B"
        }

        with self.assertRaises(acre.DynamicKeyClashError):
            acre.compute(data, allow_key_clash=False)

        # Allow to pass (even if unpredictable result)
        acre.compute(data, allow_key_clash=True)

    def test_compute_preserve_reference_to_self(self):
        """acre.compute() does not format key references to itself."""
        data = {
            "PATH": "{PATH}",
            "PYTHONPATH": "x;y/{PYTHONPATH}"
        }
        # test windows platform
        with mock.patch("os.pathsep", ";"):
            data = acre.compute(data)
            self.assertEqual(data, {
                "PATH": "{PATH}",
                "PYTHONPATH": "x;y/{PYTHONPATH}"
            })

        # test unix platforms
        with mock.patch("os.pathsep", ":"):
            data = {
                "PATH": "{PATH}",
                "PYTHONPATH": "x:y/{PYTHONPATH}"
            }
            data = acre.compute(data)
            self.assertEqual(data, {
                "PATH": "{PATH}",
                "PYTHONPATH": "x:y/{PYTHONPATH}"
            })

    def test_append(self):
        """Append paths of two environments into one."""
        data_a = {
            "A": "A\\a",
            "B": "B\\b",
            "C": "C"
        }
        data_b = {
            "A": "A2\\a2",
            "C": "C",
            "D": "D2",
        }

        # Keep unaltered copies to check afterwards the originals
        # remain unaltered by the append function
        _data_a = data_a.copy()
        _data_b = data_b.copy()

        # test windows platform
        with mock.patch("platform.system", return_value="Windows"):
            with mock.patch("os.pathsep", ";"):
                data = acre.append(data_a, data_b)

                self.assertEqual(data, {
                    "A": "A\\a;A2\\a2",
                    "B": "B\\b",
                    "C": "C",
                    "D": "D2"
                })

        # test unix platforms
        with mock.patch("platform.system", return_value="Linux"):
            with mock.patch("os.pathsep", ":"):
                with mock.patch.dict(data_a, {"A": "A/a", "B": "B/b"}):
                    with mock.patch.dict(data_b, {"A": "A2/a2"}):
                        data = acre.append(data_a, data_b)

                        self.assertEqual(data, {
                            "A": "A/a:A2/a2",
                            "B": "B/b",
                            "C": "C",
                            "D": "D2"
                        })

        # Ensure the original dicts are unaltered
        self.assertEqual(data_a, _data_a)
        self.assertEqual(data_b, _data_b)

    def test_merge(self):
        """acre.merge() merges correctly."""
        data = {
            "A": "a;{A}",
            "B": "b;c;d",
            "C": "C"
        }

        environment = {
            "A": "A",
            "C": "D"
        }

        # test Windows platform
        with mock.patch("platform.system", return_value="Windows"):
            with mock.patch("os.pathsep", ";"):
                data = acre.merge(data, current_env=environment)

                # Note that C from the environment is not preserved,
                # it's overwritten by the merge. (To preserve it should have
                # a reference to itself). See "A"
                self.assertEqual(data, {
                    "A": "a;A",
                    "B": "b;c;d",
                    "C": "C"
                })

        # test unix platforms
        with mock.patch("platform.system", return_value="Linux"):
            with mock.patch("os.pathsep", ":"):
                data = {
                    "A": "a:{A}",
                    "B": "b:c:d",
                    "C": "C"
                }
                data = acre.merge(data, current_env=environment)
                self.assertEqual(data, {
                    "A": "a:A",
                    "B": "b:c:d",
                    "C": "C"
                })

    def test_merge_formats_references_to_self(self):
        """acre.merge() correctly formats variables references to itself."""
        # Skip when not in current environment

        # test Windows platform
        with mock.patch("platform.system", return_value="Windows"):
            with mock.patch("os.pathsep", ";"):
                data = {
                    "PATH": "a;b;{PATH}",
                }
                merged = acre.merge(data, current_env={})
                self.assertEqual(merged["PATH"], "a;b;")

        # test unix platforms
        with mock.patch("platform.system", return_value="Linux"):
            with mock.patch("os.pathsep", ":"):
                data = {
                    "PATH": "a:b:{PATH}",
                }
                merged = acre.merge(data, current_env={})
                self.assertEqual(merged["PATH"], "a:b:")

        # Allow merge

        # Note that on merge the paths are *not* ensured to be unique and
        # *might* end up in the resulting variable more than once.
        # This is expected behavior.

        # test Windows platform
        with mock.patch("platform.system", return_value="Windows"):
            with mock.patch("os.pathsep", ";"):
                data = {
                    "PATH": "a;b;{PATH}"
                }

                merged = acre.merge(data, current_env={"PATH": "b;c;d"})
                self.assertEqual(merged["PATH"], "a;b;b;c;d")

        # test unix platforms
        with mock.patch("platform.system", return_value="Linux"):
            with mock.patch("os.pathsep", ":"):
                data = {
                    "PATH": "a:b:{PATH}"
                }

                merged = acre.merge(data, current_env={"PATH": "b:c:d"})
                self.assertEqual(merged["PATH"], "a:b:b:c:d")

    def test_merge_preserves_current_env(self):
        """acre.merge() preserves data in original environment."""
        data = {"A": "a"}
        environment = {"B": "b"}
        result = acre.merge(data, current_env=environment)

        self.assertEqual(result["B"], "b")

    def test_cleanup(self):
        """Test if acre.compute() cleanup function behaves correctly."""
        data = {
            "A": "FOO",
            "B": "{A}",
            "C": ":0.0",
            "D": "A;A;B;C",
            "E": "a\\A;a\\A;B;C",
            "F": "a\\A;a\\A;b\\B;c\\C",
            "G": ";;a\\A;b\\B",
            "H": ";;a;b"
        }
        expected = {
            "A": "FOO",
            "B": "FOO",
            "C": ":0.0",
            "D": "A;A;B;C",
            "E": "a\\A;a\\A;B;C",
            "F": "a\\A;b\\B;c\\C",
            "G": "a\\A;b\\B",
            "H": ";;a;b",
        }
        # test unix platforms
        with mock.patch("platform.system", return_value="Linux"):
            with mock.patch("os.pathsep", ":"):
                data.update({
                    "D": "A:A:B:C",
                    "E": "a/A:a/A:B:C",
                    "F": "a/A:a/A:b/B:c/C",
                    "G": "::a/A:b/B",
                    "H": "::a:b"
                })

                expected.update({
                    "D": "A:A:B:C",
                    "E": "a/A:a/A:B:C",
                    "F": "a/A:b/B:c/C",
                    "G": "a/A:b/B",
                    "H": "::a:b"
                })

                result = acre.compute(data, cleanup=True)
                self.assertEqual(result, expected)
