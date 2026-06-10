# mrs-build

`mrs-build` is a [`colcon`](https://colcon.readthedocs.io/en/released/) wrapper for working with ROS2 workspaces.


## Installation

### UV tool
To install as `uv` tool (system wide, but isolated dependencies), run the following:
```shell
uv tool install git+https://github.com/ctu-mrs/mrs-build
```

### Tab completion
To setup shell completions, add the following to your config (eg. `.bashrc`, for other shell, replace `bash` with your shell):
```shell
eval "$(mrs-build generate-shell-completion bash)"
```
