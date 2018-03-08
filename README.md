# env_prototype
Simple Python dynamic environment prototype

# Examples

#### Compute a dynamic environment

This sample will compute the result of a dynamic environment that
has values that use values from other keys in the environment.

```python
import env_prototype.api as api

data = {
    "MAYA_VERSION": "2018",
    "MAYA_LOCATION": "C:/Program Files/Autodesk/Maya{MAYA_VERSION}"

}

env = api.compute(data)
assert env["MAYA_LOCATION"] == "C:/Program Files/Autodesk/Maya2018"
```

This also works with recursion.

```python
import env_prototype.api as api

data = {
    "MAYA_VERSION": "2018",
    "PIPELINE": "Z:/pipeline",
    "APPS": "{PIPELINE}/apps",
    "MAYA_LOCATION": "{APPS}/Autodesk/Maya{MAYA_VERSION}"
}

env = api.compute(data)
assert env["MAYA_LOCATION"] == "Z:/pipeline/apps/Autodesk/Maya2018"
```

For more usage examples see `tests/`
