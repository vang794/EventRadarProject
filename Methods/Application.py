from polls.models import User, ApplicationStatus, Application


class ApplicationMethods:

    def create_app(self,user,message):
        if len(message) >300:
            raise ValueError("Message must be less than 3000 characters.")

        new_application = Application(
            user=user,
            message=message,
            status=ApplicationStatus.PENDING,
        )
        new_application.save()


    #check app exists through user
    def app_exists(self,app,user):
        if user is not None:
            return Application.objects.filter(user=user) is not None
    #get id
    def get_id(self, app):
        return app.id
    #get user
    def get_user(self, app):
        return app.user
    #set user
    def set_user(self, app, user):
        app.user = user
        app.save()
    #get user first name
    def get_fname(self, app):
        return app.user.first_name
    #get user last name
    def get_lfname(self, app):
        return app.user.last_name
    #get user username
    def get_username(self, app):
        return app.user.username
    #get user email
    def get_email(self, app):
        return app.user.email
    #get status
    def change_status(self, app, new_status):
        if new_status in ApplicationStatus:
            app.status = new_status
            app.save()
    #set status
    def get_status(self, app):
        return app.status
    #get message
    def get_message(self, app):
        return app.message
    #set message
    def set_message(self, app, new_message):
        app.message = new_message
        app.save()
    #get submit date and time
    def get_date_time(self, app):
        return app.submitted_at