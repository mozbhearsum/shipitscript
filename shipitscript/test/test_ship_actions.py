import pytest
from unittest.mock import MagicMock

from freezegun import freeze_time
import shipitapi
import shipitscript.ship_actions
from shipitscript.ship_actions import mark_as_shipped, mark_as_started, submit_mar_manifest


@freeze_time('2018-01-19 12:59:59')
@pytest.mark.parametrize('timeout, expected_timeout', (
    (1, 1),
    ('10', 10),
    (None, 60),
))
def test_mark_as_shipped(monkeypatch, timeout, expected_timeout):
    ReleaseClassMock = MagicMock()
    release_instance_mock = MagicMock()
    release_info = {
        'status': 'shipped',
        'shippedAt': '2018-01-19 12:59:59'
    }
    attrs = {
        'getRelease.return_value': release_info
    }
    release_instance_mock.configure_mock(**attrs)
    ReleaseClassMock.side_effect = lambda *args, **kwargs: release_instance_mock
    monkeypatch.setattr(shipitapi, 'Release', ReleaseClassMock)

    ship_it_instance_config = {
        'username': 'some-username',
        'password': 'some-password',
        'api_root': 'http://some.ship-it.tld/api/root',
    }
    if timeout is not None:
        ship_it_instance_config['timeout_in_seconds'] = timeout
    release_name = 'Firefox-59.0b1-build1'

    mark_as_shipped(ship_it_instance_config, release_name)

    ReleaseClassMock.assert_called_with(
        ('some-username', 'some-password'),
        api_root='http://some.ship-it.tld/api/root',
        timeout=expected_timeout,
    )
    release_instance_mock.update.assert_called_with(
        'Firefox-59.0b1-build1', status='shipped', shippedAt='2018-01-19 12:59:59'
    )


@pytest.mark.parametrize('timeout, expected_timeout', (
    (1, 1),
    ('10', 10),
    (None, 60),
))
def test_mark_as_started(monkeypatch, timeout, expected_timeout):
    ReleaseClassMock = MagicMock()
    NewReleaseClassMock = MagicMock()
    release_instance_mock = MagicMock()
    release_info = {
        'status': 'Started',
        'ready': True,
        'complete': True,
    }
    attrs = {
        'getRelease.return_value': release_info
    }
    release_instance_mock.configure_mock(**attrs)
    new_release_instance_mock = MagicMock()
    ReleaseClassMock.side_effect = lambda *args, **kwargs: release_instance_mock
    NewReleaseClassMock.side_effect = lambda *args, **kwargs: new_release_instance_mock
    monkeypatch.setattr(shipitapi, 'Release', ReleaseClassMock)
    monkeypatch.setattr(shipitapi, 'NewRelease', NewReleaseClassMock)

    ship_it_instance_config = {
        'username': 'some-username',
        'password': 'some-password',
        'api_root': 'http://some.ship-it.tld/api/root',
    }
    if timeout is not None:
        ship_it_instance_config['timeout_in_seconds'] = timeout

    release_name = 'Firefox-59.0b1-build1'
    data = dict(
        product='firefox',
        version='99.0b1',
        buildNumber=1,
        branch='projects/maple',
        mozillaRevision='default',
        l10nChangesets='ro default',
        partials='98.0b1,98.0b14,98.0b15',
    )

    mark_as_started(ship_it_instance_config, release_name, data)

    ReleaseClassMock.assert_called_with(
        ('some-username', 'some-password'),
        api_root='http://some.ship-it.tld/api/root',
        timeout=expected_timeout,
    )
    release_instance_mock.update.assert_called_with(
        'Firefox-59.0b1-build1', ready=True, complete=True, status="Started"
    )
    NewReleaseClassMock.assert_called_with(
        ('some-username', 'some-password'),
        api_root='http://some.ship-it.tld/api/root',
        timeout=expected_timeout,
        csrf_token_prefix='firefox-'
    )
    new_release_instance_mock.submit.assert_called_with(**data)


def test_submit_mar_manifest(monkeypatch):
    build_mar_filelist_mock = MagicMock()
    collect_mar_checksums_mock = MagicMock()
    generate_mar_manifest_mock = MagicMock()
    # These methods actually live in shipitscript.utils, but because
    # ship_actions imports them, they need to be patched there.
    monkeypatch.setattr(shipitscript.ship_actions, 'build_mar_filelist', build_mar_filelist_mock)
    monkeypatch.setattr(shipitscript.ship_actions, 'collect_mar_checksums', collect_mar_checksums_mock)
    monkeypatch.setattr(shipitscript.ship_actions, 'generate_mar_manifest', generate_mar_manifest_mock)

    ship_it_instance_config = {}
    release_name = "Firefox-63.0-build1"
    upstreamArtifacts = [
        {"taskId": "abc", "taskType": "partial", "paths": ["foo.sha512"]},
        {"taskId": "def", "taskType": "partial", "paths": ["foo.sha512"]},
    ]

    submit_mar_manifest('fake', ship_it_instance_config, release_name, upstreamArtifacts)

    build_mar_filelist_mock.assert_called_with('fake', upstreamArtifacts)
