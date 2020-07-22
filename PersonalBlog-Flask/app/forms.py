from flask_wtf import Form
from wtforms import StringField, BooleanField, TextAreaField
from wtforms.validators import DataRequired, Length
from app.models import User

class LoginForm(Form):
    # openid = StringField('openid', validators=[DataRequired()])
    nickname = StringField('nickname', validators=[DataRequired()])
    password = StringField('password', validators=[DataRequired()])
    email = StringField('email')
    remember_me = BooleanField('remember_me', default=False)

class EditForm(Form):
    nickname = StringField('nicknamae', validators=[DataRequired()])
    about_me = TextAreaField('about_me', validators=[Length(min=0, max=140)])

    def __init__(self, original_nickname, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        self.original_nickname = original_nickname

    def validate(self):
        if not Form.validate(self):
            return false
        if self.nickname.data == self.original_nickname:
            return True
        user = User.query.filter_by(nickname = self.nickname.data).first()
        if user != None:
            self.nickname.errors.append('This Name is already used! Please choose another one!')
            return False
        return True

class PostForm(Form):
    post = StringField('post', validators=[DataRequired()])