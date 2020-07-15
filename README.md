## Python dev

```shell
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Install RockDB
```shell
pip install Cython
sudo apt install build-essential libsnappy-dev \
                zlib1g-dev libbz2-dev libgflags-dev \
                librocksdb-dev liblz4-1 liblz4-dev
pip install python-rocksdb
```

## Install sowba
```shell
pip install -e .
```

## Run
```shell
uvicorn main:app --reload
```
