# Docker Container

The `Dockerfile` builds the `tarp` command and also contains PyTorch for demonstrating how to read the files.


```bash
docker build -t vidprep - < Dockerfile > build.log 2>&1; tail build.log
```

     ---> Using cache
     ---> f952bff42081
    Step 28/29 : RUN pip3 install git+git://github.com/tmbdev/webdataset
     ---> Using cache
     ---> 1cb776374cc6
    Step 29/29 : RUN apt-get install -qqy curl
     ---> Using cache
     ---> a7279aab6bea
    Successfully built a7279aab6bea
    Successfully tagged vidprep:latest


# Download Test Data

Download part of a shard, using `tarp cat` to get only the first three records. (The error message is harmless.)


```bash
./run bash -c '
    curl http://storage.googleapis.com/lpr-yt8m-lo-sharded/yt8m-lo-002999.tar | 
        tarp cat - -o testshard.tar --end=3
'
```

    # writing testshard.tar
      % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                     Dload  Upload   Total   Spent    Left  Speed
      0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0# source -
      0 54.9G    0  174M    0     0  25.9M      0  0:36:06  0:00:06  0:36:00 26.7M
    curl: (23) Failed writing body (563 != 1418)


# Splitting the Video Files

We're using `ffmpeg` to split each `.mp4` into multiple segments. We also extract metadata about the original video.

This script will be invoked by `tarp proc`, so we know that all the input info has filenames of the form `sample.*`.

We return multiple outputs in the form `sample-000000.mp4` etc.; `tarp proc -m` picks these up and turns them into new samples.


```bash
cat extract-segments
```

    #!/bin/bash
    set -e
    ls -l sample.mp4
    
    # get mp4 metadata (total length, etc.)
    ffprobe sample.mp4 -v quiet -print_format json -show_format -show_streams > sample.mp4.json
    
    # perform the rescaling and splitting
    ffmpeg -loglevel error -stats -i sample.mp4 \
        -vf "scale=512:256:force_original_aspect_ratio=decrease,pad=512:256:(ow-iw)/2:(oh-ih)/2" \
        -c:a copy -f segment -segment_time 31 -reset_timestamps 1  \
        -segment_format_options movflags=+faststart \
        sample-%06d.mp4
    
    # copy the metadata into each video fragment
    for s in sample-??????.mp4; do
        b=$(basename $s .mp4)
        cp sample.mp4.json $b.mp4.json
        cp sample.info.json $b.info.json
    done


# Run the Script over All Samples


```bash
./run tarp proc  -m $(pwd)/extract-segments testshard.tar -o testoutput.tar
```

    # writing testoutput.tar
    # source testshard.tar
    -rw-r--r-- 1 tmb tmb 40635944 Apr 16 17:25 sample.mp4
    frame= 5603 fps=737 q=-1.0 Lsize=N/A time=00:03:07.19 bitrate=N/A dup=0 drop=1 speed=24.6x    
    -rw-r--r-- 1 tmb tmb 18818304 Apr 16 17:25 sample.mp4
    frame= 4000 fps=818 q=-1.0 Lsize=N/A time=00:02:13.44 bitrate=N/A speed=27.3x    
    -rw-r--r-- 1 tmb tmb 59482703 Apr 16 17:25 sample.mp4
    frame= 7291 fps=594 q=-1.0 Lsize=N/A time=00:04:03.27 bitrate=N/A speed=19.8x    


# Checking the Output


```bash
tar tvf testoutput.tar | sed 10q
```

    -rwxr-xr-x bigdata/bigdata 31317 2020-04-16 10:25 ---2pGwkL7M/000000.info.json
    -rwxr-xr-x bigdata/bigdata 1404421 2020-04-16 10:25 ---2pGwkL7M/000000.mp4
    -rwxr-xr-x bigdata/bigdata    3985 2020-04-16 10:25 ---2pGwkL7M/000000.mp4.json
    -rwxr-xr-x bigdata/bigdata   31317 2020-04-16 10:25 ---2pGwkL7M/000001.info.json
    -rwxr-xr-x bigdata/bigdata 1370750 2020-04-16 10:25 ---2pGwkL7M/000001.mp4
    -rwxr-xr-x bigdata/bigdata    3985 2020-04-16 10:25 ---2pGwkL7M/000001.mp4.json
    -rwxr-xr-x bigdata/bigdata   31317 2020-04-16 10:25 ---2pGwkL7M/000002.info.json
    -rwxr-xr-x bigdata/bigdata 1419187 2020-04-16 10:25 ---2pGwkL7M/000002.mp4
    -rwxr-xr-x bigdata/bigdata    3985 2020-04-16 10:25 ---2pGwkL7M/000002.mp4.json
    -rwxr-xr-x bigdata/bigdata   31317 2020-04-16 10:25 ---2pGwkL7M/000003.info.json
    tar: write error



```bash
./run tarp proc -c 'ffprobe sample.mp4' --end=10 testoutput.tar -o /dev/null | grep Duration:
```

      Duration: 00:00:33.43, start: 0.065982, bitrate: 336 kb/s
      Duration: 00:00:33.44, start: 0.000000, bitrate: 327 kb/s
      Duration: 00:00:33.43, start: 0.000000, bitrate: 339 kb/s
      Duration: 00:00:25.08, start: 0.000000, bitrate: 317 kb/s
      Duration: 00:00:33.43, start: 0.000000, bitrate: 322 kb/s
      Duration: 00:00:28.52, start: 0.000000, bitrate: 325 kb/s
      Duration: 00:00:33.37, start: 0.066000, bitrate: 269 kb/s
      Duration: 00:00:33.37, start: 0.000000, bitrate: 309 kb/s
      Duration: 00:00:32.63, start: 0.000000, bitrate: 326 kb/s
      Duration: 00:00:27.43, start: 0.000000, bitrate: 363 kb/s


# Reading the Output with PyTorch


```bash
cat vidreader.py
```

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



```bash
./run python3 vidreader.py
```

    /usr/local/lib/python3.8/dist-packages/torchvision/io/video.py:106: UserWarning: The pts_unit 'pts' gives wrong results and will be removed in a follow-up version. Please use pts_unit 'sec'.
      warnings.warn("The pts_unit 'pts' gives wrong results and will be removed in a " +
    ---
    ['__key__', 'info.json', 'mp4', 'mp4.json']
    torch.Size([1000, 256, 512, 3]) torch.Size([2, 1471488])
    {'video_fps': 29.916666666666668, 'audio_fps': 44100}
    ---
    ['__key__', 'info.json', 'mp4', 'mp4.json']
    torch.Size([1000, 256, 512, 3]) torch.Size([2, 1469906])
    {'video_fps': 29.916666666666668, 'audio_fps': 44100}
    ---
    ['__key__', 'info.json', 'mp4', 'mp4.json']
    torch.Size([1000, 256, 512, 3]) torch.Size([2, 1470371])
    {'video_fps': 29.916666666666668, 'audio_fps': 44100}



```bash

```
