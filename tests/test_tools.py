import os
import unittest

import env_prototype.api as api


SAMPLES = os.path.join(os.path.dirname(__file__), "samples")


class TestTools(unittest.TestCase):

    def setup_sample(self, sample):
        os.environ["TOOL_ENV"] = os.path.join(SAMPLES, sample)

    def test_get_tools(self):
        """Get tools works"""

        self.setup_sample("sample1")
        env = api.get_tools(["global"])

        self.assertEqual(env, {
            "PIPELINE": "P:/pipeline/dev2_1"
        })

    def test_get_with_platform(self):
        """Get tools works"""

        self.setup_sample("sample1")

        env = api.get_tools(["maya_2018"], platform_name="darwin")
        self.assertEqual(env["PATH"], "{MAYA_LOCATION}/bin")

        # Test Mac only path
        self.assertTrue("DYLD_LIBRARY_PATH" in env)
        self.assertEqual(env["DYLD_LIBRARY_PATH"], "{MAYA_LOCATION}/MacOS")

        env = api.get_tools(["maya_2018"], platform_name="windows")
        self.assertEqual(env["PATH"], ";".join([
            "{MAYA_LOCATION}/bin",
            "C:/Program Files/Common Files/Autodesk Shared/",
            "C:/Program Files (x86)/Autodesk/Backburner/"])
        )

        # Test Mac only path not present in windows
        self.assertTrue("DYLD_LIBRARY_PATH" not in env)

    def test_compute_tools(self):

        self.setup_sample("sample1")
        env = api.get_tools(["maya_2018"], platform_name="windows")

        env = api.compute(env)
        self.assertEqual(env["MAYA_LOCATION"],
                         "C:/Program Files/Autodesk/Maya2018")

