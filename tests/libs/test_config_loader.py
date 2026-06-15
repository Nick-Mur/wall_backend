import unittest
import os
import json
import tempfile
from pathlib import Path
from typing import Any, Dict

from libs.config_loader import ConfigLoader, load_config


class TakeConfigLoader(unittest.TestCase):
    def setUp(self):
        """Preparation before each test: clearing environment variables"""
        self.original_environ = dict(os.environ)
        for key in list(os.environ.keys()):
            if key.startswith("TEST__") or key.startswith("APP__"):
                del os.environ[key]

    def tearDown(self):
        """Restoring environment variables after the test"""
        os.environ.clear()
        os.environ.update(self.original_environ)

    def test_should_use_default_path(self):
        """Using default path"""
        # when
        loader = ConfigLoader()

        # then
        self.assertEqual(loader.config_path, Path("config.json"))

    def test_using_custom_path(self):
        """Using custom path"""
        # when
        loader = ConfigLoader(config_path="papka/papka/config.json")

        # then
        self.assertEqual(loader.config_path, Path("papka/papka/config.json"))

    def test_should_format_env_prefix_without_underscore(self):
        """Formatting env prefix without underscore"""
        # when
        loader = ConfigLoader(env_prefix="APP")

        # then
        self.assertEqual(loader.env_prefix, "APP__")

    def test_should_format_env_prefix_with_underscore(self):
        """Formatting env prefix with underscore"""
        # when
        loader = ConfigLoader(env_prefix="__APP_____")

        # then
        self.assertEqual(loader.env_prefix, "APP__")

    def test_should_use_empty_env(self):
        """Using empty env by default"""
        # when
        loader = ConfigLoader()

        # then
        self.assertEqual(loader.env_prefix, "")

    def test_should_return_empty_if_not_config(self):
        """Returning empty dict if config file is not exists"""
        # given
        loader = ConfigLoader(config_path="non_existent_file.json")

        # when
        result = loader.read_config_file()

        # then
        self.assertEqual(result, {})

    def test_should_load_valid_config(self):
        """Loading valid config"""
        # given
        config_data = {"host": "localhost", "port": 8080}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            json.dump(config_data, tmp)
            tmp_path = tmp.name

        loader = ConfigLoader(config_path=tmp_path)

        # when
        result = loader.read_config_file()

        # then
        self.assertEqual(result, config_data)

        # cleanup
        Path(tmp_path).unlink()

    def test_should_return_empty_dict_if_json_invalid(self):
        """Returning empty value when invalid config"""
        # given
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as tmp:
            tmp.write('{"invalid": json}')
            tmp_path = tmp.name

        loader = ConfigLoader(config_path=tmp_path)

        # when
        result = loader.read_config_file()

        # then
        self.assertEqual(result, {})

        # cleanup
        Path(tmp_path).unlink()

    def test_should_format_env_key_without_prefix(self):
        """Formatting key without prefix"""
        # given
        loader = ConfigLoader()

        # when
        result = loader.format_env_key("DB__HOST")

        # then
        self.assertEqual(result, ["db", "host"])

    def test_should_format_env_key_with_prefix(self):
        """Formatting key with prefix"""
        # given
        loader = ConfigLoader(env_prefix="APP")

        # when
        result = loader.format_env_key("APP__DB__HOST")

        # then
        self.assertEqual(result, ["db", "host"])

    def test_should_remove_empty_parts_from_env_key(self):
        """Delete whitespaces in key"""
        # given
        loader = ConfigLoader()

        # when
        result = loader.format_env_key("  DB  __  HOST  ")

        # then
        self.assertEqual(result, ["db", "host"])

    def test_should_lowercase_env_key_parts(self):
        """Lowercase key"""
        # given
        loader = ConfigLoader()

        # when
        result = loader.format_env_key("DaTaBaSE__HOSt")

        # then
        self.assertEqual(result, ["database", "host"])

    def test_should_set_nested_value(self):
        """Setting nested value"""
        # given
        loader = ConfigLoader()
        target = {}
        path = ["database", "host"]
        value = "localhost"

        # when
        loader.set_nested(target, path, value)

        # then
        self.assertEqual(target, {"database": {"host": "localhost"}})

    def test_should_cast_false_to_bool(self):
        """Set bool type"""
        # given
        loader = ConfigLoader()

        # then
        self.assertIs(loader.cast_type("false"), False)
        self.assertIs(loader.cast_type("False"), False)
        self.assertIs(loader.cast_type("FALSE"), False)

    def test_should_cast_null_to_none(self):
        """Set None type"""
        # given
        loader = ConfigLoader()

        # then
        self.assertIs(loader.cast_type("null"), None)
        self.assertIs(loader.cast_type("None"), None)
        self.assertIs(loader.cast_type("NULL"), None)

    def test_should_cast_integer_string_to_int(self):
        """Set int type"""
        # given
        loader = ConfigLoader()

        # then
        self.assertEqual(loader.cast_type("42"), 42)
        self.assertEqual(loader.cast_type("-10"), -10)
        self.assertEqual(loader.cast_type("0"), 0)

    def test_should_cast_float_string_to_float(self):
        """Set float type"""
        # given
        loader = ConfigLoader()

        # then
        self.assertEqual(loader.cast_type("3.14"), 3.14)
        self.assertEqual(loader.cast_type("-0.5"), -0.5)

    def test_should_cast_json_array_to_list(self):
        """Cast json array to list"""
        # given
        loader = ConfigLoader()

        # then
        self.assertEqual(loader.cast_type("[1, 2, 3]"), [1, 2, 3])
        self.assertEqual(loader.cast_type('["a", "b"]'), ["a", "b"])

    def test_should_cast_json_object_to_dict(self):
        """Cast json obj to dict"""
        # given
        loader = ConfigLoader()

        # then
        self.assertEqual(loader.cast_type('{"name": "John"}'), {"name": "John"})
        self.assertEqual(loader.cast_type('{"x": 1, "y": 2}'), {"x": 1, "y": 2})

if __name__ == "__main__":
    unittest.main()