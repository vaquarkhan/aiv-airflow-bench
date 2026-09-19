# specific language governing permissions and limitations
# under the License.
function cleanup_runner {
    set -euo pipefail
    set -x
    echo "Checking free space before Docker relocation"
    df -H
    # Note:
    # Disk layout on x86_64 (2026-01):
    # Hence we only move docker to /mnt on x86_64 where we have a separate /mnt mount
    # If we get short on disk space on arm64 as well we need to revisit this logic
    # and make the idle nvme being used as well.
    if uname -i | grep -q x86_64; then
        local target_docker_volume_location="/mnt/var-lib-docker"
        # This is faster than docker prune. The normal caller has just cleaned /mnt.
        # Retain the recursive ownership repair if another caller reuses a nonempty target.
        sudo systemctl stop docker
        sudo rm -rf /var/lib/docker
        sudo mkdir -p "${target_docker_volume_location}" /var/lib/docker
        sudo mount --bind "${target_docker_volume_location}" /var/lib/docker
        local remaining
        remaining="$(sudo find "${target_docker_volume_location}" -mindepth 1 -maxdepth 1 -print -quit)"
        if [[ -n "${remaining}" ]]; then
            sudo chown -R 0:0 "${target_docker_volume_location}"
        else
            sudo chown 0:0 "${target_docker_volume_location}"
        fi
        sudo systemctl start docker
        echo "Checking free space after Docker relocation"
        df -H
    fi
}
