#!/usr/bin/env python3
import os, subprocess
import click
from pathlib import Path

LIB_PATH = Path("tool")
os.environ["PATH"] = str(LIB_PATH) + os.pathsep + os.environ["PATH"]

def run(cmd):
    try:
        env = os.environ.copy()
        env['PYTHONIOENCODING'] = 'utf-8'
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8', errors='replace', env=env)
        out, err = proc.communicate()
        if proc.returncode != 0:
            click.echo(f"[{cmd[0]}] Error: {err}", err=True)
            return None
        return out.strip()
    except Exception as e:
        click.echo(f"Command Error: {str(e)}", err=True)
        return None

@click.group()
def cli():
    pass

@cli.group()
def info():
    pass

@info.command()
def show():
    out = run(["ideviceinfo"])
    if out:
        for line in out.splitlines():
            if ':' in line:
                k, v = line.split(':', 1)
                click.echo(f"{k.strip()}: {v.strip()}")
    else:
        click.echo("No device detected.")

@cli.group()
def apps():
    pass

@apps.command()
def list():
    out = run(["ideviceinstaller", "-l"])
    if out: click.echo("Installed apps:\n" + out)

@apps.command()
@click.argument('ipa_file')
def install(ipa_file):
    if not Path(ipa_file).is_file():
        click.echo("Error: IPA file does not exist.", err=True)
        return
    if run(["ideviceinstaller", "-i", ipa_file]):
        click.echo("Install succeeded.")

@apps.command()
@click.argument('bundle_id')
def uninstall(bundle_id):
    if run(["ideviceinstaller", "-U", bundle_id]):
        click.echo("Uninstall succeeded.")

@cli.group()
def device():
    pass

@device.command()
def reboot():
    if run(["idevicediagnostics", "restart"]):
        click.echo("Device is rebooting.")

@device.command()
def shutdown():
    if run(["idevicediagnostics", "shutdown"]):
        click.echo("Device is shutting down.")

@device.command(name="enter-recovery")
def enter_recovery():
    udid_output = run(["idevice_id", "-l"])
    if not udid_output:
        click.echo("No device found. Please connect your iOS device.", err=True)
        return
    udid = udid_output.splitlines()[0]
    click.echo(f"Detected UDID: {udid}")
    if run(["ideviceenterrecovery", udid]):
        click.echo("Device should now be in recovery mode.")

@device.command(name="exit-recovery")
def exit_recovery():
    if run(["irecovery", "-n"]):
        click.echo("Exit Recovery command sent. Device should reboot.")

if __name__ == '__main__':
    cli()