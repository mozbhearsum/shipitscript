import logging
from datetime import datetime

import shipitapi

from shipitscript.utils import (
    get_auth_primitives, check_release_has_values
)


log = logging.getLogger(__name__)


def mark_as_shipped(ship_it_instance_config, release_name):
    """Function to make a simple call to Ship-it API to change a release
    status to 'shipped'
    """
    auth, api_root, timeout_in_seconds = get_auth_primitives(ship_it_instance_config)
    release_api = shipitapi.Release(auth, api_root=api_root, timeout=timeout_in_seconds)
    shipped_at = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')

    log.info('Marking the release as shipped with {} timestamp...'.format(shipped_at))
    release_api.update(release_name, status='shipped', shippedAt=shipped_at)
    check_release_has_values(release_api, release_name,
                             status='shipped', shippedAt=shipped_at)


def mark_as_started(ship_it_instance_config, release_name, data):
    """Function to make two consecutive calls to Ship-it v1; simulates the
    RelMan `Do eeet` behavior by submitting the HTML response whilst the
    second one marks the release as started - similar to what Release
    Runner would do"""
    auth, api_root, timeout_in_seconds = get_auth_primitives(ship_it_instance_config)

    product = data['product']
    new_release = shipitapi.NewRelease(auth, api_root=api_root,
                                       timeout=timeout_in_seconds,
                                       csrf_token_prefix='{}-'.format(product))
    log.info('Submitting the release to Ship-it v1 ...')
    new_release.submit(**data)

    log.info('Marking the release as started ...')
    release_api = shipitapi.Release(auth, api_root=api_root,
                                    timeout=timeout_in_seconds)
    release_api.update(release_name, ready=True, complete=True, status="Started")
    check_release_has_values(release_api, release_name,
                             ready=True, complete=True, status="Started")


# TODO: This needs to talk to ship it v2
def submit_file_signing_manifest(context, ship_it_instance_config, release_name):
    filelist = build_mar_filelist(context.config['work_dir'], context.task['payload']['checksums_artifacts'])
    mar_checksums = collect_mar_checksums(filelist)
    # set up ship it v2 auth
    # collect data from upstream task artifacts
    #  - we probably can't depend directly on all of the upstream tasks, because there will be too many...
    #  - it looks like release-generate-checksums has mozharness pulling stuff from s3.
    #     we should avoid this if we can, because it bypasses CoT. ideally we find some way to depend on
    #     everything directly here....
    #    or maybe there's intermediary "dummy" tasks that download checksums from their upstreams, and make larger checksums
    #    out of those. then we could depend on those, and pull all of those checksums.
    #    would that still be useful if those "dummy" tasks run on docker worker, though?
