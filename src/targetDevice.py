import multiprocessing
import pathlib
import os
import sox
import json


class InformationForCopy:
    def __init__(
        self, file, index, targetDirectory, options={}, startsecond=None, endsecond=None
    ):
        self.source = pathlib.Path(file)
        self.target = pathlib.Path(targetDirectory) / (str(index) + ".wav")
        self.options = options
        self.startsecond = startsecond
        self.endsecond = endsecond


def __copy(copyInfomation: InformationForCopy):
    t = sox.Transformer()
    if not (copyInfomation.startsecond is None or copyInfomation.endsecond is None):
        t.trim(start_time=copyInfomation.startsecond, end_time=copyInfomation.endsecond)
    t.remix(num_output_channels=1)
    t.gain(gain_db=-1.3, normalize=True)
    t.bass(gain_db=1)
    t.loudness(gain_db=-1)
    t.pad()
    t.set_output_format(
        file_type="wav", rate=32000, bits=16, channels=1, encoding="signed-integer"
    )
    t.set_globals(dither=True, multithread=True)

    t.build(
        input_filepath=str(copyInfomation.source),
        output_filepath=str(copyInfomation.target),
    )

    return copyInfomation

def readSDCardContent(path: pathlib.Path):
    content = {}
    for i in range(9):
        filepath = path / str(i) / "content.json"
        if filepath.is_file():
            with open(filepath, mode="r") as f:
                content[str(i)] = json.load(f)
    return content

def writeInfoToJson(copyInformationList):
    data_to_dump = {f.target.name: f.source.name for f in copyInformationList}
    with open(copyInformationList[0].target.parent / "content.json", mode="w") as f:
        json.dump(
            data_to_dump, f, indent=3,
        )


class PoolProgress:
    def __init__(self, pool, job):
        self.task = pool._cache[job._job]
        self.job = job
        self.result = pool.apply_async(job.get)

    def remainingJobs(self):
        return self.task._number_left

    def wait(self):
        self.job.wait()

    def get(self):
        return self.result.get()


# returns PoolProgress
def startProcessing(copyInformationList):
    pool = multiprocessing.Pool(os.cpu_count() - 1)
    asyncObject = pool.map_async(__copy, copyInformationList, callback=writeInfoToJson)
    return PoolProgress(pool, asyncObject)

def checkSDDir(path: pathlib.Path):
    if not path.is_dir():
        return False
    return all([(path / str(i)).is_dir() for i in range(9)])
