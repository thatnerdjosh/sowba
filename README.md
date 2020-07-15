## Developments


### Clone repo
```shell
git clone https://github.com/oukone/sowba.git && cd sowba
```

### Create virtual env
```shell
python -m venv venv
source venv/bin/activate
```

### Install RockDB dependencies
```shell
sudo apt install build-essential libsnappy-dev \
                zlib1g-dev libbz2-dev libgflags-dev \
                librocksdb-dev liblz4-1 liblz4-dev
```

### Install sowba
```shell
pip install -e .
```

### Run
```shell
uvicorn main:app --reload
```
