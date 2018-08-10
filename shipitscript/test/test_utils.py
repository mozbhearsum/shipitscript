import os
import os.path
import pytest
import tempfile
from unittest.mock import MagicMock

from scriptworker.exceptions import ScriptWorkerTaskException, \
    TaskVerificationError
from shipitscript.utils import (
    get_auth_primitives, check_release_has_values, same_timing,
    build_mar_filelist
)


@pytest.yield_fixture(scope='function')
def tmpdir():
    with tempfile.TemporaryDirectory() as tmp:
        yield tmp


@pytest.mark.parametrize('ship_it_instance_config,expected', (
    ({
        'api_root': 'http://some-ship-it.url',
        'timeout_in_seconds': 1,
        'username': 'some-username',
        'password': 'some-password'
    }, (('some-username', 'some-password'), 'http://some-ship-it.url', 1)),
    ({
        'api_root': 'http://some-ship-it.url',
        'username': 'some-username',
        'password': 'some-password'
    }, (('some-username', 'some-password'), 'http://some-ship-it.url', 60)),
))
def test_get_auth_primitives(ship_it_instance_config, expected):
    assert get_auth_primitives(ship_it_instance_config) == expected


@pytest.mark.parametrize('release_info,  values, raises', (
    ({
        'name': 'Fennec-X.0bX-build42',
        'shippedAt': '2018-07-03T09:19:00+00:00',
        'mh_changeset': '',
        'mozillaRelbranch': None,
        'version': 'X.0bX',
        'branch': 'projects/maple',
        'submitter': 'shipit-scriptworker-stage',
        'ready': True,
        'mozillaRevision': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'release_eta': None,
        'starter': None,
        'complete': True,
        'submittedAt': '2018-07-02T09:18:39+00:00',
        'status': 'shipped',
        'comment': None,
        'product': 'fennec',
        'description': None,
        'buildNumber': 42,
        'l10nChangesets': {},
    }, {
        'status': 'shipped',
        'shippedAt': '2018-07-03 09:19:00',
    }, False),
    ({
        'name': 'Fennec-X.0bX-build42',
        'shippedAt': '2018-07-03T09:19:00+00:00',
        'mh_changeset': '',
        'mozillaRelbranch': None,
        'version': 'X.0bX',
        'branch': 'projects/maple',
        'submitter': 'shipit-scriptworker-stage',
        'ready': True,
        'mozillaRevision': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'release_eta': None,
        'starter': None,
        'complete': True,
        'submittedAt': '2018-07-02T09:18:39+00:00',
        'status': 'Started',
        'comment': None,
        'product': 'fennec',
        'description': None,
        'buildNumber': 42,
        'l10nChangesets': {},
    }, {
        'status': 'shipped',
        'shippedAt': '2018-07-03 09:19:00',
    }, True),
    ({
        'name': 'Fennec-X.0bX-build42',
        'shippedAt': '2018-07-03T09:19:01+00:00',
        'mh_changeset': '',
        'mozillaRelbranch': None,
        'version': 'X.0bX',
        'branch': 'projects/maple',
        'submitter': 'shipit-scriptworker-stage',
        'ready': True,
        'mozillaRevision': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'release_eta': None,
        'starter': None,
        'complete': True,
        'submittedAt': '2018-07-02T09:18:39+00:00',
        'status': 'shipped',
        'comment': None,
        'product': 'fennec',
        'description': None,
        'buildNumber': 42,
        'l10nChangesets': {},
    }, {
        'status': 'shipped',
        'shippedAt': '2018-07-03 09:19:00',
    }, True),
    ({
        'name': 'Fennec-X.0bX-build42',
        'shippedAt': '2018-07-03T09:19:01+00:00',
        'mh_changeset': '',
        'mozillaRelbranch': None,
        'version': 'X.0bX',
        'branch': 'projects/maple',
        'submitter': 'shipit-scriptworker-stage',
        'ready': True,
        'mozillaRevision': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'release_eta': None,
        'starter': None,
        'complete': True,
        'submittedAt': '2018-07-02T09:18:39+00:00',
        'status': 'shipped',
        'comment': None,
        'product': 'fennec',
        'description': None,
        'buildNumber': 42,
        'l10nChangesets': {},
    }, {
        'status': 'shipped',
        'shippedAt': '2018-07-02 08:03:00',
    }, True),
    ({
        'name': 'Fennec-X.0bX-build42',
        'shippedAt': '2018-07-03T09:19:01+00:00',
        'mh_changeset': '',
        'mozillaRelbranch': None,
        'version': 'X.0bX',
        'branch': 'projects/maple',
        'submitter': 'shipit-scriptworker-stage',
        'ready': True,
        'mozillaRevision': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'release_eta': None,
        'starter': None,
        'complete': True,
        'submittedAt': '2018-07-02T09:18:39+00:00',
        'status': 'Started',
        'comment': None,
        'product': 'fennec',
        'description': None,
        'buildNumber': 42,
        'l10nChangesets': {},
    }, {
        'ready': True,
        'complete': True,
        'status': 'Started',
    }, False),
    ({
        'name': 'Fennec-X.0bX-build42',
        'shippedAt': '2018-07-03T09:19:01+00:00',
        'mh_changeset': '',
        'mozillaRelbranch': None,
        'version': 'X.0bX',
        'branch': 'projects/maple',
        'submitter': 'shipit-scriptworker-stage',
        'ready': None,
        'mozillaRevision': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'release_eta': None,
        'starter': None,
        'complete': True,
        'submittedAt': '2018-07-02T09:18:39+00:00',
        'status': 'Started',
        'comment': None,
        'product': 'fennec',
        'description': None,
        'buildNumber': 42,
        'l10nChangesets': {},
    }, {
        'ready': True,
        'complete': True,
        'status': 'Started',
    }, True),
    ({
        'name': 'Fennec-X.0bX-build42',
        'shippedAt': '2018-07-03T09:19:01+00:00',
        'mh_changeset': '',
        'mozillaRelbranch': None,
        'version': 'X.0bX',
        'branch': 'projects/maple',
        'submitter': 'shipit-scriptworker-stage',
        'ready': True,
        'mozillaRevision': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'release_eta': None,
        'starter': None,
        'complete': False,
        'submittedAt': '2018-07-02T09:18:39+00:00',
        'status': 'Started',
        'comment': None,
        'product': 'fennec',
        'description': None,
        'buildNumber': 42,
        'l10nChangesets': {},
    }, {
        'ready': True,
        'complete': True,
        'status': 'Started',
    }, True),
    ({
        'name': 'Fennec-X.0bX-build42',
        'shippedAt': '2018-07-03T09:19:01+00:00',
        'mh_changeset': '',
        'mozillaRelbranch': None,
        'version': 'X.0bX',
        'branch': 'projects/maple',
        'submitter': 'shipit-scriptworker-stage',
        'ready': True,
        'mozillaRevision': 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa',
        'release_eta': None,
        'starter': None,
        'complete': False,
        'submittedAt': '2018-07-02T09:18:39+00:00',
        'status': None,
        'comment': None,
        'product': 'fennec',
        'description': None,
        'buildNumber': 42,
        'l10nChangesets': {},
    }, {
        'ready': True,
        'complete': True,
        'status': 'Started',
    }, True),
))
def test_generic_validation(monkeypatch, release_info,  values, raises):
    release_name = "Fennec-X.0bX-build42"
    ReleaseClassMock = MagicMock()
    attrs = {
        'getRelease.return_value': release_info
    }
    ReleaseClassMock.configure_mock(**attrs)

    if raises:
        with pytest.raises(ScriptWorkerTaskException):
            check_release_has_values(ReleaseClassMock, release_name, **values)
    else:
        check_release_has_values(ReleaseClassMock, release_name, **values)


@pytest.mark.parametrize('time1,time2, expected', (
    ('2018-07-02 16:51:04', '2018-07-02T16:51:04+00:00', True),
    ('2018-07-02 16:51:04', '2018-07-02T16:51:04+01:00', False),
    ('2018-07-02 16:51:04', '2018-07-02T16:51:04+00:11', False),
    ('2018-07-02 16:51:04', '2018-07-02T16:51:04', True),
))
def test_same_timing(time1, time2, expected):
    assert same_timing(time1, time2) == expected


@pytest.mark.parametrize('present_files, checksums_artifacts, expected_exception', (
    (
     ("abc/foo.sha512", "def/foo.sha512"),
     [
        {"taskId": "abc", "path": "foo.sha512"},
        {"taskId": "def", "path": "foo.sha512"},
     ],
     None,
    ),
    (
     ("abc/foo.sha512", "def/foo.sha512"),
     [
        {"taskId": "abc", "path": "foo.sha512"},
        {"taskId": "def", "path": "foo.sha512"},
        {"taskId": "ghi", "path": "foo.sha512"},
     ],
     TaskVerificationError,
    ),
))
def test_build_mar_filelist(tmpdir, present_files, checksums_artifacts, expected_exception):
    workdir = tmpdir
    for a in present_files:
        abs_path = os.path.join(workdir, 'cot', a)
        os.makedirs(os.path.dirname(abs_path))
        with open(abs_path, 'w') as f:
            # Make file exist
            print('something', file=f)
    try:
        file_list = build_mar_filelist(workdir, checksums_artifacts)
        expected_mars = []
        for a in checksums_artifacts:
            expected_mars.append((a['path'], os.path.join(workdir, 'cot', a['taskId'], a['path'])))
        assert set(file_list) == set(expected_mars)
        return
    except BaseException as e:
        if isinstance(e, expected_exception):
            # The correct exception was raised!
            return
        # We expected an exception and got the one we expected - nothing to do!
        assert False, "expected exception ({}) not raised".format(expected_exception)
        return
    if expected_exception:
        assert False, "expected exception ({}) not raised".format(expected_exception)
