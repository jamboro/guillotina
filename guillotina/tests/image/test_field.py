from guillotina.contrib.image.behaviors import IImageAttachment
from guillotina.contrib.image.behaviors import IMultiImageAttachment
from guillotina.tests.image import TEST_DATA_LOCATION

import json
import os
import pytest


pytestmark = pytest.mark.asyncio


@pytest.mark.app_settings(
    {"applications": ["guillotina", "guillotina.contrib.image"], "cloud_datamanager": "db"}
)
async def test_image_field_with_behavior(redis_container, container_requester):
    async with container_requester as requester:
        _, status = await requester("POST", "/db/guillotina/@addons", data=json.dumps({"id": "image"}))
        assert status == 200

        response, status = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps(
                {"@type": "Item", "@behaviors": [IImageAttachment.__identifier__], "id": "foobar"}
            ),
        )
        assert status == 201

        response, status = await requester("GET", "/db/guillotina/foobar/@download/image")
        assert status == 404

        with open(os.path.join(TEST_DATA_LOCATION, "profile.jpg"), "rb") as image:
            data = image.read()
            size = len(data)

        response, status = await requester(
            "PATCH",
            "/db/guillotina/foobar/@upload/image",
            data=data,
            headers={"x-upload-size": f"{size}"},
        )
        assert status == 200

        response, status = await requester("GET", "/db/guillotina/foobar/@download/image")
        assert status == 200
        assert len(response) == size

        response, status = await requester("GET", "/db/guillotina/foobar/@images/image/thumb")
        assert status == 204

        response, status = await requester("PATCH", "/db/guillotina/foobar/@images/image/thumb")
        assert status == 200

        response, status = await requester("PATCH", "/db/guillotina/foobar/@images/image/icon")
        assert status == 200

        response, status = await requester("PATCH", "/db/guillotina/foobar/@images/image/nono")
        assert status == 404

        response, status = await requester("GET", "/db/guillotina/foobar/@images/image/thumb")
        assert status == 200

        assert len(response) < size
        assert len(response) == 5260

        response, status = await requester("GET", "/db/guillotina/foobar/@images/image/icon")
        assert status == 200

        assert len(response) < size
        assert len(response) == 1915

        with open(os.path.join(TEST_DATA_LOCATION, "logo.png"), "rb") as image:
            data = image.read()
            size = len(data)

        response, status = await requester(
            "PATCH",
            "/db/guillotina/foobar/@upload/image",
            data=data,
            headers={"x-upload-size": f"{size}"},
        )
        assert status == 200

        response, status = await requester("GET", "/db/guillotina/foobar/@images/image/thumb")
        assert status == 204

        response, status = await requester("PATCH", "/db/guillotina/foobar/@images/image/thumb")
        assert status == 200

        response, status = await requester("GET", "/db/guillotina/foobar/@images/image/thumb")
        assert status == 200

        response, status = await requester("DELETE", "/db/guillotina/foobar/@delete/image")
        assert status == 200

        response, status = await requester("GET", "/db/guillotina/foobar/@download/image")
        assert status == 404


@pytest.mark.app_settings(
    {"applications": ["guillotina", "guillotina.contrib.image"], "cloud_datamanager": "db"}
)
async def test_multiimage_field_with_behavior(redis_container, container_requester):
    async with container_requester as requester:
        _, status = await requester("POST", "/db/guillotina/@addons", data=json.dumps({"id": "image"}))
        assert status == 200

        response, status = await requester(
            "POST",
            "/db/guillotina/",
            data=json.dumps(
                {"@type": "Item", "@behaviors": [IMultiImageAttachment.__identifier__], "id": "foobar"}
            ),
        )
        assert status == 201

        with open(os.path.join(TEST_DATA_LOCATION, "profile.jpg"), "rb") as image:
            data = image.read()
            size = len(data)

        response, status = await requester(
            "PATCH",
            "/db/guillotina/foobar/@upload/images/key1",
            data=data,
            headers={"x-upload-size": f"{size}"},
        )
        assert status == 200

        response, status = await requester("GET", "/db/guillotina/foobar/@images/images/key1/thumb")
        assert status == 204

        response, status = await requester("PATCH", "/db/guillotina/foobar/@images/images/key1/thumb")
        assert status == 200

        response, status = await requester("GET", "/db/guillotina/foobar/@images/images/key1/thumb")
        assert status == 200
