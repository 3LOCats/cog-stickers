import yaml

def run_command(command):
    import subprocess
    if isinstance(command, list):
        command = ' '.join(command)

    print(f"Running: {command}")
    proc = subprocess.Popen(command, shell=True)
    proc.wait()

def install_packages(cuda:bool=False):
    with open('cog.yaml', 'r') as file:
        config = yaml.safe_load(file).get('build')

    if cuda:
        torch_versions = {
            "torch": "2.2.2",
            "torchvision": "0.17.2",
            "torchaudio":"2.2.2",
        }

        cuda_version=config['cuda'].replace('.', '')

        cuda_pkgs = []
        pkgs=[]
        for pkg in config['python_packages']:
            if pkg.startswith('torch'):
                if pkg in torch_versions:
                    cuda_pkgs.append(f"{pkg}=={torch_versions[pkg]}+cu{cuda_version}")
                else:
                    cuda_pkgs.append(pkg)
            else:
                pkgs.append(pkg)
        cuda_pkgs.append(f'--extra-index-url https://download.pytorch.org/whl/cu{cuda_version} -U')
        pkgs.append('cog')

        run_command(f"pip install -q {' '.join(cuda_pkgs)}")

    run_command(['python', '-m', 'pip install -q', {' '.join(pkgs)}])

    for r in config['run']:
        run_command(r)

def reset_project():
    run_command('./scripts/reset.sh')

def download_weights():
    import json

    from scripts.weights_from_workflow import handle_weights
    with open('sticker_maker_api.json', 'r') as f:
        workflow = json.load(f)
        weights = handle_weights(workflow)

    print('Installing weights:')
    print('\n'.join(weights))
    run_command(['python', './scripts/get_weights.py', {' '.join(weights)}])

def start_server():
    run_command('python -m cog.server.http')

async def async_start_server():
    import asyncio

    async def create_command(cmd: str):
        proc = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        return proc

    async def wait_command(proc):
        stdout, stderr = await proc.communicate()
        print(f"stdout: {stdout.decode()}")
        print(f"stderr: {stderr.decode()}")

        return_code = await proc.wait()
        print(f"Return code: {return_code}")

    http_server = await create_command("python -m cog.server.http")
    print(f'http server pid: {http_server.pid}')
    wait_command(http_server)

def predict(
        prompt:str='rabbit',
        negative_prompt:str='',
        width:int=1024,
        height:int=1024,
        steps:int=20,
        number_of_images:int=1,
        output_format:str='png',
        output_quality:int=100,
        seed:int=None,
        sticker_type:str='Sticker' # 'Sticker' or 'Stickersheet'
):
    from predict import Predictor

    p = Predictor()
    p.setup()

    files=p.predict(
        prompt=prompt,
        negative_prompt=negative_prompt,
        width=width,
        height=height,
        steps=steps,
        number_of_images=number_of_images,
        output_format=output_format,
        output_quality=output_quality,
        sticker_type=sticker_type,
        seed=seed
        )
    return files
