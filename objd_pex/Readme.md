#OBJD with Pex

## Virtual Environment Creation 

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install the virtualenv package:

```bash
pip3 install virtualenv
```

Create the Environment for Detectron2:

```bash
virtualenv --python=/usr/bin/python3.6 detectron_env
```

Activate the virtual environment:

```bash
source detectron_env/bin/activate
```

Install the required packages from requirements.txt:

```bash
pip install -r objd_requirements.txt
```

Install torch, torchvision and torch audio:

```bash
pip3 install torch==1.10.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

pip3 install torchvision==0.11.2+cpu torchaudio==0.10.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html
```

Install detectron2:

```bash
python -m pip install detectron2 -f https://dl.fbaipublicfiles.com/detectron2/wheels/cpu/torch1.10/index.html
```

Install flask:

```bash
pip install flask
```

Make new requirements for using pex:

```bash
pip freeze > application_requirements.txt

pip install pex

pex --python=python3.6 -r application_requirements.txt -o application_name.pex
```


