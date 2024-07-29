import sys
import os
import argparse

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

def run_command(command):
    import subprocess
    if isinstance(command, list):
        command = ' '.join(command)

    print(f"Running: {command}")
    proc = subprocess.Popen(command, shell=True)
    proc.wait()

def install_packages(install_cuda:bool=True, install_others=True):
    import yaml
    with open('cog.yaml', 'r') as file:
        config = yaml.safe_load(file).get('build')

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
                cuda_pkgs.append(f"{pkg}>={torch_versions[pkg]}+cu{cuda_version}")
            else:
                cuda_pkgs.append(pkg)
        else:
            pkgs.append(pkg)
    cuda_pkgs.append(f'--extra-index-url https://download.pytorch.org/whl/cu{cuda_version} -U')
    pkgs.append('cog')

    if install_cuda:
        run_command(["pip install -q", ' '.join(cuda_pkgs)])

    if install_others:
        run_command(['python', '-m', 'pip install -q', ' '.join(pkgs)])

        for r in config['run']:
            run_command(r)

def reset_project():
    run_command('./scripts/reset.sh')

def download_weights():
    import json

    from weights_from_workflow import handle_weights
    with open('sticker_maker_api.json', 'r') as f:
        workflow = json.load(f)
        weights = handle_weights(workflow)

    print('Installing weights:')
    print('\n'.join(weights))
    run_command(['python', './scripts/get_weights.py', ' '.join(weights)])

def start_server():
    run_command('nohup python -m cog.server.http &')

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


def main():
    parser = argparse.ArgumentParser(description='sticker maker command line tool.')
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')

    parser_setup = subparsers.add_parser('setup', help='setup the project')
    parser_setup.add_argument('-a', '--all', action='store_true', help='install all dependencies')
    parser_setup.add_argument('-p', '--packages', action='store_true', help='install python packages')
    parser_setup.add_argument('-r', '--reset', action='store_true', help='calling reset.sh to reset the project')
    parser_setup.add_argument('-w', '--weights', action='store_true', help='download weights')

    parser_server = subparsers.add_parser('server', help='start/stop http server')
    parser_server.add_argument('-s', '--start', action='store_true', help='start http server')

    parser_predict = subparsers.add_parser('predict', help='download weights')
    parser_predict.add_argument('-t', '--sticker_type', default='Sticker', choices=['Sticker', 'Stickersheet'], help='The sticker type to generate an image.')
    parser_predict.add_argument('-i', '--input_file', help='Specify input parameters to generate an image.')

    args = parser.parse_args()


    if args.command == 'setup':
        print('Setting up the project')
        if args.all or not any([args.packages, args.reset, args.weights]):
            print('Installing all dependencies')
            install_packages()
            print('Resetting the project')
            reset_project()
            print('Downloading weights')
            download_weights()
        else:
            if args.packages:
                print('Installing python packages')
                install_packages()
            if args.reset:
                print('Resetting the project')
                reset_project()
            if args.weights:
                print('Downloading weights')
                download_weights()
    elif args.command == 'server':
        print('Starting the server')
        start_server()
    elif args.command == 'predict':
        if args.input_file:
            print('Predicting the image using the input file')
            with open(args.input_file, 'r') as f:
                import json
                input_params = json.load(f)
                predict(**input_params)
        else:
            print(f'Predicting the image, sticker type: {args.sticker_type}')
            predict(sticker_type=args.sticker_type)

if __name__ == "__main__":
    main()
