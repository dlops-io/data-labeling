import os
import asyncio
import pandas as pd
import traceback
import time


async def run():
    try:
        print("CLI....")
        total_start_time = time.time()

        print("************** Complete ****************")
        execution_time = (time.time() - total_start_time) / 60.0
        print("Total execution time (mins)", execution_time)

    except Exception as e:
        print(e)
        traceback.print_exc()


asyncio.run(run())
