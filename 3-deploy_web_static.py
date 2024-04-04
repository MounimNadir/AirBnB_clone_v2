#!/usr/bin/python3
"""
Fabric script based on the file 2-do_deploy_web_static.py that creates and
distributes an archive to the web servers
"""

from fabric.api import env, local, put, run
from datetime import datetime
from os.path import basename, isdir
from fabric.exceptions import NetworkError

env.hosts = ['142.44.167.228', '144.217.246.195']

def do_pack():
    """Generates a tgz archive"""
    try:
        date = datetime.now().strftime("%Y%m%d%H%M%S")
        if not isdir("versions"):
            local("mkdir -p versions")
        file_name = "versions/web_static_{}.tgz".format(date)
        local("tar -cvzf {} web_static".format(file_name))
        return file_name
    except Exception as e:
        print("Error occurred during packaging:", e)
        return None

def do_deploy(archive_path):
    """Distributes an archive to the web servers"""
    try:
        if not archive_path or not basename(archive_path).endswith('.tgz'):
            return False
        file_n = basename(archive_path)
        no_ext = file_n.split(".")[0]
        remote_path = "/data/web_static/releases/{}/".format(no_ext)
        put(archive_path, '/tmp/')
        run('mkdir -p {}'.format(remote_path))
        run('tar -xzf /tmp/{} -C {}'.format(file_n, remote_path))
        run('rm /tmp/{}'.format(file_n))
        run('mv {}{}/web_static/* {}{}/'.format(remote_path, no_ext, remote_path, no_ext))
        run('rm -rf {}{}/web_static'.format(remote_path, no_ext))
        run('rm -rf /data/web_static/current')
        run('ln -s {} /data/web_static/current'.format(remote_path))
        return True
    except NetworkError as ne:
        print("Network error occurred:", ne)
        return False
    except Exception as e:
        print("Error occurred during deployment:", e)
        return False

def deploy():
    """Creates and distributes an archive to the web servers"""
    archive_path = do_pack()
    if archive_path:
        return do_deploy(archive_path)
    else:
        return False

