import torch
import torchvision
import webdataset as wds
from itertools import islice
import tempfile

url = "testoutput.tar"

def mp4decode(data):
    with tempfile.TemporaryDirectory() as dname:
        with open(dname+"/sample.mp4", "wb") as stream:
            stream.write(data)
        vframes, aframes, info = torchvision.io.read_video(dname+"/sample.mp4")
    return vframes, aframes, info

dataset = (
    wds.Dataset(url)
    .decode()
    .map_dict(mp4=mp4decode)
)

for sample in islice(dataset, 0, 3):
    print("---")
    print(list(sample.keys()))
    vframes, aframes, info = sample["mp4"]
    print(vframes.shape, aframes.shape)
    print(info)
