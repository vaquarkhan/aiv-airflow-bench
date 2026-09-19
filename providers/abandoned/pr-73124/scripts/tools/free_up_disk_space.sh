# specific language governing permissions and limitations
# under the License.

set -euo pipefail

COLOR_BLUE=$'\e[34m'
COLOR_RESET=$'\e[0m'

echo "${COLOR_BLUE}Disk space before cleanup${COLOR_RESET}"
df -H

echo "${COLOR_BLUE}Freeing up disk space${COLOR_RESET}"

# These directories are independent. Removing them concurrently shortens the fixed
# cleanup cost paid by every CI/PROD image consumer while preserving exactly the
# same cleanup set. Cap concurrency to avoid turning deletion into disk thrashing.
cleanup_targets=(
    /usr/share/dotnet/
    /usr/local/graalvm/
    /usr/local/.ghcup/
    /usr/local/share/powershell
    /usr/local/share/chromium
    /usr/local/share/boost
    /usr/local/lib/android
    /opt/hostedtoolcache
    /opt/ghc
)
printf '%s\0' "${cleanup_targets[@]}" | xargs -0 -r -n 1 -P 4 sudo rm -rf --

# apt's cache is independent of the directories above; keep it explicit so any
# failure still fails the cleanup step rather than being hidden in a background job.
sudo apt-get clean

echo "${COLOR_BLUE}Disk space after cleanup${COLOR_RESET}"
df -H
