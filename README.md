# Acre

**Acre** is a lightweight cross-platform environment management Python
package that makes it trivial to launch applications in their own
configurable working environment.

## Examples

#### Compute a dynamic environment `acre.compute`

This sample will compute the result of a dynamic environment that
has values that use values from other keys in the environment.

To compute the result of a dynamic environment use `acre.compute`

```python
import acre

data = {
    "MAYA_VERSION": "2018",
    "MAYA_LOCATION": "C:/Program Files/Autodesk/Maya{MAYA_VERSION}"

}

env = acre.compute(data)
assert env["MAYA_LOCATION"] == "C:/Program Files/Autodesk/Maya2018"
```

This also works with recursion.

```python
import acre

data = {
    "MAYA_VERSION": "2018",
    "PIPELINE": "Z:/pipeline",
    "APPS": "{PIPELINE}/apps",
    "MAYA_LOCATION": "{APPS}/Autodesk/Maya{MAYA_VERSION}"
}

env = acre.compute(data)
assert env["MAYA_LOCATION"] == "Z:/pipeline/apps/Autodesk/Maya2018"
```

#### Platform specific paths `acre.parse`

You can set up your data with platform specific paths, by using a
dictionary. These need to be parsed with `acre.parse`

```python
import acre

data = {
    "VERSION": "2018",
    "MY_LOCATION": {
        "windows": "C:/path/on/windows/{VERSION}",
        "darwin": "/path/on/mac/osx/{VERSION}",
        "linux": "/path/on/linux/{VERSION}"
    }
}

env = acre.parse(data, platform_name="windows")
assert env["MY_LOCATION"] == "C:/path/on/windows/{VERSION}"

env = acre.compute(env)
assert env["MY_LOCATION"] == "C:/path/on/windows/2018"

# When *not* explicitly providing a platform name, the current active
# platform is used. So for your active OS:
env = acre.parse(data)
env = acre.compute(env)
print(env["MY_LOCATION"])
```

#### Apply the environment on your system

The final touch for getting your environment ready and in use is to
merge it with your environment. So:

```python
import os
import acre

data = {
    "PIPELINE": {
        "windows": "P:/pipeline",
        "darwin": "//share/pipeline",
        "linux": "//share/pipeline",
    },
    "CUSTOMPATH": "{PATH}",
    "DATAPATH": "{PIPELINE}/mydata"
}

# Parse the platform specific variables
env = acre.parse(data, platform_name="windows")

# Compute the dynamic environment
env = acre.compute(env)

# Merge it with your local environment
env = acre.merge(env, current_env=os.environ)

# Update your local environment
os.environ.update(env)

# Now it's live!
assert os.environ["DATAPATH"] == "P:/pipeline/mydata"
```

#### More samples?

For more usage examples see `tests/`
