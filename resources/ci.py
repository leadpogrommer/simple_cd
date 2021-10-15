import threading

import werkzeug.exceptions as exceptions
from flask import request
from flask.views import MethodView
from flask_jwt_extended import get_jwt_identity, jwt_required

from database.models import Project, User
from utils.project import DockerProject


def launch_task(f):
    thread = threading.Thread(target=f)
    thread.start()


# Yes, I know that this is a shitty lock and there are potential race conditions
def get_project(f):
    @jwt_required()
    def internal(self, id):
        try:
            project = Project.objects.get(id=id)
            user_id = get_jwt_identity()
            # print(str(project.creator.id, user_id)
            if str(project.creator.id) != user_id:
                raise exceptions.NotFound()
        except Exception:
            raise exceptions.NotFound()

        return f(self, DockerProject(project))

    return internal


def lock(f):
    def internal(self, project: DockerProject):
        if project.dbo.locked:
            return {"status": "busy"}
        project.dbo.locked = True
        project.dbo.save()
        return f(self, project)

    return internal


class CreatorApi(MethodView):
    @jwt_required()
    def post(self):
        data = request.get_json()
        project = Project(**data)
        project.project_status = 'updating'
        project.runtime_status = 'stopped'
        project.creator = User.objects.get(id=get_jwt_identity())
        project.save()

        def callback():
            dp = DockerProject(project)
            dp.init_repo()
            dp.build_image()
            project.locked = False
            project.save()

        launch_task(callback)
        return {"id": str(project.id)}


class ProjectApi(MethodView):
    @get_project
    def get(self, project: DockerProject):
        return {"status": project.image_status, "ready": not project.dbo.locked}

    @get_project
    @lock
    def delete(self, project: DockerProject):

        def callback():
            project.stop_container()
            project.delete_image()
            project.remove_repo()
            project.dbo.delete()

        launch_task(callback)
        return {"status": "ok"}

    @get_project
    @lock
    def post(self, project: DockerProject):
        def callback():
            try:
                project.stop_container()
                project.update_repo()
                project.build_image()
            finally:
                project.dbo.unlock()
            project.start_container()

        launch_task(callback)
        return {"status": "ok"}


class RuntimeApi(MethodView):
    @get_project
    def get(self, project):
        return {"status": project.container_status, "ready": not project.dbo.locked, "logs": project.dbo.logs}

    @get_project
    @lock
    def post(self, project: DockerProject):
        def callback():
            project.dbo.unlock()
            project.start_container()

        launch_task(callback)
        return {"status": "ok"}

    @get_project
    @lock
    def delete(self, project: DockerProject):
        def callback():
            try:
                project.stop_container()
                project.dbo.logs = ''
                project.dbo.save()
            finally:
                project.dbo.unlock()

        launch_task(callback)
        return {"status": "ok"}
