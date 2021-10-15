import pathlib
import shutil

from docker import DockerClient
from docker.errors import NotFound, ImageNotFound
from docker.models.containers import Container, Image
from git import Repo

from database.models import Project

dc = DockerClient()
basepath = pathlib.Path(__file__).parent.parent


class DockerProject:
    def __init__(self, p: Project):
        self.dbo = p
        if p.id is None:
            raise Exception("Project must be saved to db")
        self.repo_path = basepath.joinpath("repos").joinpath(str(self.dbo.id))
        self.image_tag = f'ci-{str(self.dbo.id)}'
        self.container_name = self.image_tag

    @property
    def container_status(self):
        try:
            cont = dc.containers.get(self.container_name)  # type: Container
            return cont.status
        except NotFound:
            return "not_exists"

    @property
    def image_status(self):
        try:
            dc.images.get(self.image_tag)  # type: Image
            return "exists"
        except ImageNotFound:
            return "not_exists"

    def init_repo(self):
        Repo.clone_from(self.dbo.repo, self.repo_path, single_branch=True, branch=self.dbo.branch)

    def remove_repo(self):
        shutil.rmtree(self.repo_path)

    def update_repo(self):
        Repo(self.repo_path).remotes[0].pull()

    def delete_image(self):
        try:
            dc.images.remove(image=self.image_tag, force=True)
        except ImageNotFound:
            pass

    def build_image(self):
        self.delete_image()
        i, ls = dc.images.build(path=str(self.repo_path.resolve()), rm=True, forcerm=True,
                                buildargs={'COMMAND': self.dbo.command}, dockerfile='../../project.Dockerfile',
                                tag=f'ci-{str(self.dbo.id)}')
        for l in ls:
            print(l)

    def start_container(self):
        self.dbo.logs = ''
        self.dbo.save()
        self.stop_container()
        cont = dc.containers.run(image=self.image_tag, auto_remove=False, name=self.container_name,
                                 detach=True)  # type: Container
        for l in cont.logs(stream=True):
            self.dbo.logs += str(l)
            self.dbo.save()

    def stop_container(self):
        try:
            cont = dc.containers.get(self.container_name)  # type: Container
            cont.remove(force=True)
        except NotFound:
            pass
