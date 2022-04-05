"""
Map Tasks
---------

A map task lets you run a pod task or a regular task over a list of inputs within a single workflow node.
This means you can run thousands of instances of the task without creating a node for every instance, providing valuable performance gains!

Some use cases of map tasks include:

* Several inputs must run through the same code logic
* Multiple data batches need to be processed in parallel
* Hyperparameter optimization

Let's look at an example now!
"""

# %%
# First, we import the libraries.
import typing

from flytekit import Resources, map_task, task, workflow
from flytekit.types.file import FlyteFile

# %%
# Next, we define a task that we will use in our map task.
#
# .. note::
#   A map task can only accept one input and produce one output.
@task
def a_mappable_task(a: int) -> str:
    inc = a + 2
    stringified = str(inc)
    return stringified


# %%
# We also define a task to reduce the mapped output to a string.
@task
def coalesce(b: typing.List[str]) -> str:
    coalesced = "".join(b)
    return coalesced


# %%
# We send ``a_mappable_task`` to be repeated across a collection of inputs to the :py:func:`~flytekit:flytekit.map_task` function.
# In our example, ``a`` of type ``typing.List[int]`` is the input.
# The task ``a_mappable_task`` is run for each element in the list.
#
# ``with_overrides`` is useful to set resources for individual map task.
@workflow
def my_map_workflow(a: typing.List[int]) -> str:
    mapped_out = map_task(a_mappable_task)(a=a).with_overrides(
        requests=Resources(mem="300Mi"),
        limits=Resources(mem="500Mi"),
        retries=1,
    )
    coalesced = coalesce(b=mapped_out)
    return coalesced


@task
def print_and_return_last_file(task_params: typing.Dict[str, FlyteFile]) -> FlyteFile:
    ff = None
    for k, f in task_params.items():
        ff = f
        print(f"Opening file {k}")
        with open(f) as fh:
            contents = fh.read()
        print(f"Contents of {f.remote_source}:\n{contents}")

    return ff


@workflow
def map_wf(in1: typing.List[typing.Dict[str, FlyteFile]]) -> typing.List[FlyteFile]:
    return map_task(print_and_return_last_file)(task_params=in1)


# %%
# Lastly, we can run the workflow locally!
if __name__ == "__main__":
    # result = my_map_workflow(a=[1, 2, 3, 4, 5])
    # print(f"{result}")

    file_map = {
        "a": FlyteFile("/Users/ytong/tmp/a"),
        "b": FlyteFile("/Users/ytong/tmp/b"),
        "c": FlyteFile("/Users/ytong/tmp/c"),
    }
    # result_file = print_and_return_last_file(task_params=file_map)
    # print(result_file)

    file_map2 = {
        "a": FlyteFile("/Users/ytong/tmp/a"),
        "b": FlyteFile("/Users/ytong/tmp/b"),
        "c": FlyteFile("/Users/ytong/tmp/c"),
    }

    wf_output = map_wf(in1=[file_map, file_map2])
    print(wf_output)


# %%
# Map tasks can run on alternate execution backends, such as `AWS Batch <https://aws.amazon.com/batch/>`__,
# which is a provisioned service that can scale to great sizes.
