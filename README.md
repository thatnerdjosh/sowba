## Developments

### Install dependencies

#### Poetry

```shell
sudo apt -y install python3-distutils python3-venv
```

#### RocksDB

```shell
https://github.com/facebook/rocksdb/wiki/Building-on-Windows
sudo apt install build-essential libsnappy-dev \
                zlib1g-dev libbz2-dev libgflags-dev \
                librocksdb-dev liblz4-1 liblz4-dev
```

### Clone repo
```shell
git clone https://github.com/oukone/sowba.git && cd sowba
```

### Create virtual env && Install sowba
```shell
poetry install
poetry shell
```

### Run
```shell
sowba create soutra --storage=rocksdb --auth --output="/tmp/"
sowba service add menber
sowba run
```
