import vk_api
import sys
import time


class Kinder:
    def __init__(self, log=None, passw=None, token=None):
        """создаёт сессию разными способами"""
        self.vk = None
        self.token = token
        self.login = log
        self.password = passw
        if self.login and self.password:
            vk_session = vk_api.VkApi(self.login, self.password)
            try:
                vk_session.auth(token_only=True)
            except vk_api.AuthError as error_msg:
                print(error_msg)
                sys.exit()

            self.vk = vk_session.get_api()

        if self.token:
            vk_session = vk_api.VkApi(token=self.token)
            self.vk = vk_session.get_api()
            try:
                self.users_get()
            except vk_api.exceptions.ApiError as error_msg:
                print(error_msg)
                sys.exit()

    def users_get(self, id_=None):
        try:
            some_user = self.vk.users.get(user_ids=id_, fields='sex, bdate, city, relation')
            time.sleep(0.3)
        except vk_api.exceptions.ApiError as error_msg:
            print(error_msg)
            return

        return some_user

    def get_prof_photos(self, id_):
        try:
            profile = self.vk.photos.get(owner_id=id_, album_id='profile', extended=1)
            time.sleep(0.3)
        except vk_api.exceptions.ApiError as error_msg:
            print(error_msg)
            return

        return profile

    def search(self, params):
        tool = vk_api.tools.VkTools(self.vk)
        try:
            res = tool.get_all_iter('users.search', 1000, values=params)
        except vk_api.exceptions.ApiError as error_msg:
            print(error_msg)
            return

        return res

