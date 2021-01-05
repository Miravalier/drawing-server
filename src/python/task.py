import asyncio


background_tasks = []


async def init():
    # Start all background tasks
    for task in background_tasks:
        asyncio.create_task(task())


def task(parameter=None):
    # Task is called like a function
    if parameter is None or isinstance(parameter, (int, float)):
        def task_decorator(func):
            async def wrapper():
                while True:
                    if parameter is not None:
                        await asyncio.sleep(parameter)
                    result = await func()
                    if result is not None and not result:
                        break
            background_tasks.append(wrapper)
            return wrapper
        return task_decorator
    # Task is used as a standalone decorator
    else:
        async def wrapper():
            while True:
                result = await parameter()
                if result is not None and not result:
                    break
        background_tasks.append(wrapper)
        return wrapper
