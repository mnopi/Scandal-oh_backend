# # -*- coding: utf-8 -*-
from services.models import *
from tests.factories import *
from tests.fixtures.input_data import comment_text_list
from tests.testcase_classes import RequestTestCase


class CrudCommentTest(RequestTestCase):
    resource_name = 'comment'

    def test_create_comment(self):
        # given
        CommentFactory.create_batch(2)
        # when
        data = {
            "user": "/api/v1/user/1/",
            "photo": "/api/v1/photo/1/",
            "text": "This is a comment bla bla bla"
        }
        self._post(data)
        # then
        self._assert_post_ok_201()
        new_comment = Comment.objects.all().order_by('id').reverse()[0]
        assert new_comment.text == "This is a comment bla bla bla"
        assert new_comment.user == CustomUser.objects.get(pk=new_comment.user.id)
        assert new_comment.photo == Photo.objects.get(pk=new_comment.photo.id)
        assert new_comment.id is not None

    def test_create_invalid_comment(self):
        # given
        CustomUserFactory()
        PhotoFactory()
        # when
        for text in comment_text_list['invalids']:
            data = {
                "user": "/api/v1/user/1/",
                "photo": "/api/v1/photo/1/",
                "text": text
            }
            self._post(data)
            # then
            self._assert_error_response()

    def test_read_comment_list(self):
        # given
        CommentFactory.create_batch(2)
        # when
        self._get_list()
        # then
        self._assert_get_ok()
        self._assert_resp_obj_has_length(2)

    def test_read_comment(self):
        # given
        CommentFactory()
        # when
        self._get_element(1)
        # then
        self._assert_get_ok()
        self._assert_resp_obj_has_key_not_none('photo')

    def test_update_comment(self):
        # given
        CommentFactory(text='comment original blahblah')
        # when
        self._put(1, {'text': 'comment edited!!'})
        # then
        self._assert_put_ok()
        self._assert_resp_obj_has_key_equals_to('text', 'comment edited!!')

    def test_delete_comment(self):
        # given
        CommentFactory()
        # when
        self._delete(1)
        # then
        self._assert_delete_ok()
        assert Comment.objects.all().count() == 0

